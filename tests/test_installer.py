import configparser
import shutil
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'zelixins'))
import installer_support as policy
from desktop_catalog import desktops_for, compatible_greeters
import myself as installer


class PolicyTests(unittest.TestCase):
    def test_desktop_and_explicit_greeters(self):
        for desktop, default in policy.GREETERS.items():
            self.assertEqual(policy.selected_greeter(desktop, 'default'), default)
            for override in compatible_greeters([desktop]):
                self.assertEqual(policy.selected_greeter([desktop], override), override)

    def test_bios_rejects_uefi_bootloaders(self):
        for boot in ('Systemd-boot', 'Refind'):
            with self.assertRaises(ValueError):
                policy.validate_choices(100 * 1024**3, False, boot, ['linux'], True, [])
        policy.validate_choices(100 * 1024**3, False, 'Grub', ['linux'], False, [])

    def test_empty_kernel_small_disk_and_multilib_conflicts(self):
        for size, kernels, packages in ((0, ['linux'], []), (10 * 1024**3, ['linux'], []),
                                        (100 * 1024**3, [], []), (100 * 1024**3, ['linux'], ['steam'])):
            with self.assertRaises(ValueError):
                policy.validate_choices(size, True, 'Grub', kernels, False, packages)
        # Current Arch repository places Wine in extra; it does not require multilib.
        policy.validate_choices(100 * 1024**3, True, 'Grub', ['linux'], False, ['wine'])

    def test_partition_bounds_and_home(self):
        for size in (25, 26, 50, 100, 1000):
            for uefi in (False, True):
                for kernels in range(1, 5):
                    parts = policy.build_partitions(size * 1024**3, uefi, kernels)
                    end = 1
                    for p in parts:
                        self.assertEqual(p['start']['value'], end)
                        self.assertGreater(p['size']['value'], 0)
                        end += p['size']['value']
                    self.assertLess(end, size * 1024)
                    self.assertEqual(parts[0]['fs_type'], 'fat32' if uefi else 'ext4')
                    self.assertEqual('esp' in parts[0]['flags'], uefi)
                    self.assertEqual(len({p['obj_id'] for p in parts}), len(parts))
        self.assertEqual(len(policy.build_partitions(25 * 1024**3, True, 4)), 2)
        self.assertEqual(len(policy.build_partitions(100 * 1024**3, True, 1)), 3)

    def test_partition_device_names(self):
        for disk, expected in (('/dev/sda', '/dev/sda2'), ('/dev/nvme0n1', '/dev/nvme0n1p2'),
                               ('/dev/mmcblk0', '/dev/mmcblk0p2')):
            self.assertEqual(policy.partition_path(disk, 2), expected)

    def test_multilib_toggle_and_other_repositories(self):
        original = '[core]\nInclude = mirrors\n#[multilib]\n#Include = mirrors\n[zelixrepo]\nServer = custom\n'
        enabled = policy.configure_multilib(original, True)
        self.assertIn('[multilib]\nInclude = mirrors', enabled)
        self.assertEqual(policy.configure_multilib(enabled, False), original)
        self.assertEqual(policy.configure_multilib(enabled, True), enabled)
        self.assertTrue(policy.configure_multilib('[core]\n', True).endswith('Include = /etc/pacman.d/mirrorlist\n'))


class ConfigTests(unittest.TestCase):
    def combo(self, text, data=None):
        return NS(currentText=lambda: text, currentData=lambda: data)

    def generate(self, desktop, greeter, boot, multilib, size=100):
        desktops = [desktop] if isinstance(desktop, str) else list(desktop)
        desktop_page = NS(selected_desktops=lambda: desktops,
                          selected_greeter=lambda: policy.selected_greeter(desktops, greeter))
        system = NS(kb_combo=self.combo('trq'), tz_combo=self.combo('Europe/Istanbul'),
                    selected_bootloader=lambda: boot, selected_kernels=lambda: ['linux', 'linux-lts'])
        extra = NS(get_selected_packages=lambda: [], is_multilib_enabled=lambda: multilib)
        main = NS(system_page=system, desktop_page=desktop_page,
                  mirror_page=NS(get_selected_regions=lambda: ['Turkey']),
                  disk_page=NS(disk_combo=self.combo('/dev/testdisk (100G)')),
                  user_page=NS(users=[], root_pass=NS(text=lambda: '')),
                  extra_page=extra, cleanup_install_files=lambda: None)
        page = NS(main_window=main, _build_package_list=installer.SummaryPage._build_package_list,
                  _build_custom_commands=installer.SummaryPage._build_custom_commands)
        result = NS(stdout=json.dumps({'blockdevices': [{'type': 'disk', 'mountpoints': [None]}]}))
        with patch.object(installer, 'is_uefi', return_value=boot != 'BIOS'), \
             patch.object(installer, 'get_disk_size_bytes', return_value=size * 1024**3), \
             patch.object(installer.os.path, 'exists', return_value=True), \
             patch.object(installer.subprocess, 'run', return_value=result):
            self.assertTrue(installer.SummaryPage.generate_json(page))
        try:
            config = json.loads(Path(main.install_config_path).read_text())
            self.assertEqual(Path(main.install_creds_path).stat().st_mode & 0o777, 0o600)
            return config, main.install_target
        finally:
            Path(main.install_config_path).unlink()
            Path(main.install_creds_path).unlink()

    def test_generated_configuration_matrix(self):
        for desktop in policy.GREETERS:
            for greeter in ('default', *compatible_greeters([desktop])):
                for boot in ('Grub', 'Systemd-boot', 'Refind'):
                    for multilib in (False, True):
                        with self.subTest(desktop=desktop, greeter=greeter, boot=boot, multilib=multilib):
                            config, target = self.generate(desktop, greeter, boot, multilib)
                            effective = policy.selected_greeter(desktop, greeter)
                            self.assertEqual(config['profile_config']['greeter'], effective)
                            self.assertEqual(target['greeter'], effective)
                            self.assertEqual(target['desktops'], [desktops_for([desktop])[0].slug])
                            self.assertEqual(config['profile_config']['profile']['details'], [desktops_for([desktop])[0].profile])
                            self.assertNotIn(None, config['packages'])
                            self.assertEqual(config['additional_repositories'], ['multilib'] if multilib else [])
                            self.assertEqual(target['multilib'], str(multilib).lower())
                            self.assertEqual(config['custom_commands'], [])
                            self.assertEqual(target['home'], '/dev/testdisk3')
                            self.assertEqual('grub' in config['packages'], boot == 'Grub')
                            self.assertEqual('sddm-kcm' in config['packages'], effective == 'sddm')

    def test_no_invented_disks_or_sizes_after_probe_failure(self):
        with patch.object(installer.subprocess, 'run', side_effect=OSError('probe failed')):
            self.assertEqual(installer.scan_disks(), [])
            self.assertEqual(installer.get_disk_size_bytes('/dev/missing'), 0)


class ResultTests(unittest.TestCase):
    def test_archinstall_failure_never_runs_postinstall(self):
        page = MagicMock()
        installer.InstallProgressPage.process_finished(page, 1, installer.QProcess.ExitStatus.NormalExit)
        page.run_post_install.assert_not_called()
        page.install_failed.assert_called_once()

    def test_archinstall_success_starts_postinstall_before_success_ui(self):
        page = MagicMock()
        installer.InstallProgressPage.process_finished(page, 0, installer.QProcess.ExitStatus.NormalExit)
        page.run_post_install.assert_called_once()
        page.finish_btn.show.assert_not_called()

    def test_postinstall_failure_never_shows_success(self):
        page = MagicMock(log_path='/tmp/test.log')
        installer.InstallProgressPage.post_install_finished(page, 1, installer.QProcess.ExitStatus.NormalExit)
        page.finish_btn.show.assert_not_called()
        page.install_failed.assert_called_once()

    def test_success_requires_normal_exit(self):
        page = MagicMock(log_path='/tmp/test.log')
        installer.InstallProgressPage.post_install_finished(page, 0, installer.QProcess.ExitStatus.CrashExit)
        page.finish_btn.show.assert_not_called()
        page.install_failed.assert_called_once()

    def test_success_cleans_credentials(self):
        page = MagicMock()
        installer.InstallProgressPage.post_install_finished(page, 0, installer.QProcess.ExitStatus.NormalExit)
        page.finish_btn.show.assert_called_once()
        page.main_window.cleanup_install_files.assert_called_once()


class FirstLoginTests(unittest.TestCase):
    def test_apply_once_per_user_and_retry_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            bin_dir = base/'bin'
            bin_dir.mkdir()
            for command in ('busctl', 'plasma-apply-lookandfeel', 'plasma-apply-colorscheme',
                            'plasma-apply-wallpaperimage', 'kwriteconfig6'):
                p = bin_dir/command
                p.write_text('#!/bin/bash\nprintf "%s %s\\n" "${0##*/}" "$*" >> "$CALLS"\n'
                             '[[ ${FAIL_COMMAND:-} != "${0##*/}" ]]\n')
                p.chmod(0o755)
            env = dict(os.environ, HOME=directory, XDG_STATE_HOME=str(base/'state'),
                       XDG_CURRENT_DESKTOP='KDE', PATH=str(bin_dir)+':'+os.environ['PATH'],
                       CALLS=str(base/'calls'))
            script = str(ROOT/'iso_root/airootfs/usr/local/bin/zelix-first-login')
            marker = base/'state/zelix/aurora-v1.done'
            failed = subprocess.run(['bash', script], env=dict(env, FAIL_COMMAND='plasma-apply-colorscheme'))
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(marker.exists())
            subprocess.run(['bash', script], env=env, check=True)
            self.assertTrue(marker.exists())
            calls = (base/'calls').read_text()
            self.assertIn('plasma-apply-colorscheme ZelixAurora', calls)
            self.assertIn('plasma-apply-colorscheme --accent-color #ffffff\n', calls)
            subprocess.run(['bash', script], env=env, check=True)
            self.assertEqual((base/'calls').read_text(), calls)
            self.assertTrue((base/'state/zelix/appearance.log').exists())

    def test_other_desktops_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(['bash', str(ROOT/'iso_root/airootfs/usr/local/bin/zelix-first-login')],
                           env=dict(os.environ, HOME=directory, XDG_STATE_HOME=directory,
                                    XDG_CURRENT_DESKTOP='GNOME'), check=True)
            self.assertEqual(list(Path(directory).iterdir()), [])

class InstalledKDEToolTests(unittest.TestCase):
    @unittest.skipUnless(all(shutil.which(tool) for tool in (
        'plasma-apply-lookandfeel', 'plasma-apply-colorscheme', 'kwriteconfig6')),
        'Plasma tools are not installed')
    def test_real_tools_preserve_zelix_palette_and_white_accent(self):
        # Every user path and the session bus are isolated; never touch the host desktop.
        with tempfile.TemporaryDirectory(prefix='zelix-palette-test-') as directory:
            env = dict(os.environ, HOME=directory, XDG_CONFIG_HOME=directory+'/config',
                       XDG_DATA_HOME=directory+'/data', XDG_CACHE_HOME=directory+'/cache',
                       XDG_DATA_DIRS=str(ROOT/'iso_root/airootfs/usr/share')+':/usr/share',
                       QT_QPA_PLATFORM='offscreen', DISPLAY='', WAYLAND_DISPLAY='',
                       DBUS_SESSION_BUS_ADDRESS='unix:path='+directory+'/no-session-bus')
            for args in (['plasma-apply-lookandfeel', '--apply', 'org.zelixos.aurora.desktop'],
                         ['plasma-apply-colorscheme', 'ZelixAurora'],
                         ['plasma-apply-colorscheme', '--accent-color', '#ffffff'],
                         ['kwriteconfig6', '--file', 'kdeglobals', '--group', 'General',
                          '--key', 'AccentColor', '255,255,255']):
                subprocess.run(args, env=env, check=True, capture_output=True, timeout=20)
            conf = configparser.ConfigParser()
            conf.read(directory+'/config/kdeglobals')
            self.assertEqual(conf['General']['ColorScheme'], 'ZelixAurora')
            self.assertEqual(conf['General']['AccentColor'], '255,255,255')
            self.assertEqual(conf['Colors:Window']['BackgroundNormal'], '16,16,18')
            self.assertEqual(conf['KDE']['LookAndFeelPackage'], 'org.zelixos.aurora.desktop')


if __name__ == '__main__':
    unittest.main()
