import itertools
import configparser
import importlib.util
import shutil
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'zelixins'))
from desktop_catalog import (DESKTOPS, GREETER_NAMES, compatible_greeters, choose_greeter,
                             desktops_for, find_image)
import desktop_setup
import desktop_theme
import myself
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QApplication
import test_installer as installer_tests


def combinations():
    names = [desktop.name for desktop in DESKTOPS]
    for size in range(1, len(names)+1):
        yield from itertools.combinations(names, size)


class DesktopPolicyTests(unittest.TestCase):
    def test_all_127_nonempty_combinations_use_exact_intersection(self):
        total = 0
        for names in combinations():
            expected = set.intersection(*(set(desktops_for([name])[0].greeters) for name in names))
            self.assertEqual(set(compatible_greeters(names)), expected)
            self.assertIn(choose_greeter(names), expected)
            for greeter in GREETER_NAMES:
                if greeter in expected:
                    self.assertEqual(choose_greeter(names, greeter), greeter)
                else:
                    with self.assertRaises(ValueError):
                        choose_greeter(names, greeter)
            total += 1
        self.assertEqual(total, 127)

    def test_missing_unknown_or_incompatible_selection_is_rejected(self):
        for names in ([], ['Unknown']):
            with self.assertRaises(ValueError):
                choose_greeter(names)
        with self.assertRaises(ValueError):
            choose_greeter(['GNOME', 'Hyprland'], 'gdm')
        self.assertNotIn('lightdm-gtk-greeter', compatible_greeters(['Xfce4', 'Hyprland']))

    def test_empty_intersection_is_handled(self):
        first, second = MagicMock(), MagicMock()
        first.greeters = ('sddm',)
        second.greeters = ('gdm',)
        with patch('desktop_catalog.desktops_for', return_value=[first, second]):
            self.assertEqual(compatible_greeters(['a', 'b']), [])
            with self.assertRaises(ValueError):
                choose_greeter(['a', 'b'])

    def test_profile_names_and_slug_roundtrip(self):
        self.assertEqual(desktops_for(['bspwm'])[0].profile, 'Bspwm')
        self.assertEqual(desktops_for(['KDE Plasma','kde-plasma']), [DESKTOPS[0]])
        for desktop in DESKTOPS:
            self.assertEqual(desktops_for([desktop.slug])[0].name, desktop.name)


class MultiDesktopConfigTests(unittest.TestCase):
    combo = installer_tests.ConfigTests.combo
    generate = installer_tests.ConfigTests.generate

    def test_all_combinations_reach_archinstall_and_postinstall(self):
        for names in combinations():
            config, target = self.generate(names, 'default', 'Grub', False)
            expected = desktops_for(names)
            self.assertEqual(config['profile_config']['profile']['details'], [d.profile for d in expected])
            self.assertEqual(target['desktops'], [d.slug for d in expected])
            self.assertIn(target['greeter'], compatible_greeters(names))
            self.assertEqual(len(config['packages']), len(set(config['packages'])))
            custom = config['profile_config']['profile']['custom_settings']
            for desktop in expected:
                if desktop.slug in {'hyprland','sway'}:
                    self.assertEqual(custom[desktop.profile]['seat_access'], 'systemd-logind')


class DesktopUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.internet = patch.object(myself, 'check_internet', return_value=True)
        self.internet.start()
        self.window = myself.MainWindow()
        self.page = self.window.desktop_page

    def tearDown(self):
        self.window.welcome_page.refresh_timer.stop()
        self.page.asset_timer.stop()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.internet.stop()
        myself.set_language('en')

    def select(self, names):
        for desktop, checkbox in self.page.checkboxes.items():
            checkbox.setChecked(desktop in names)

    def test_nine_steps_and_named_navigation(self):
        self.assertEqual(len(self.window.pages), 9)
        self.window.stacked_widget.setCurrentWidget(self.window.system_page)
        self.window.next_page()
        self.assertIs(self.window.stacked_widget.currentWidget(), self.page)
        self.assertEqual(self.page.selected_desktops(), ['KDE Plasma'])

    def test_invalidated_greeter_is_replaced_and_empty_selection_blocks_next(self):
        self.select(['GNOME'])
        self.page.greeter_combo.setCurrentIndex(self.page.greeter_combo.findData('gdm'))
        self.page.checkboxes['Hyprland'].setChecked(True)
        self.assertEqual(self.page.selected_greeter(), 'sddm')
        self.assertNotEqual(self.page.greeter_combo.findData('gdm'), 0)
        self.assertIn('previous', self.page.status.text().lower())
        self.select([])
        self.assertFalse(self.page.next_btn.isEnabled())
        self.assertEqual(self.page.greeter_combo.count(), 0)

    def test_assets_can_be_added_late_without_losing_selection(self):
        self.select(['KDE Plasma','GNOME'])
        with tempfile.TemporaryDirectory() as directory:
            self.page.asset_root = Path(directory)
            self.page.refresh_assets(force=True)
            button = self.page.cards['kde-plasma']['preview']
            self.assertFalse(button.isEnabled())
            previews = Path(directory)/'previews'
            previews.mkdir()
            image = QImage(320,180,QImage.Format.Format_RGB32)
            image.fill(0x112233)
            self.assertTrue(image.save(str(previews/'kde-plasma.png')))
            self.page.refresh_assets()
            self.assertTrue(button.isEnabled())
            self.assertEqual(self.page.selected_desktops(), ['KDE Plasma','GNOME'])
            with patch('desktop_page.QDialog.exec', return_value=0) as dialog:
                button.click()
                dialog.assert_called_once()
            (previews/'kde-plasma.png').write_bytes(b'broken')
            self.page.refresh_assets()
            self.assertFalse(button.isEnabled())

    def test_translation_preserves_choices_and_button_background(self):
        self.select(['KDE Plasma','Xfce4'])
        self.page.greeter_combo.setCurrentIndex(self.page.greeter_combo.findData('ly'))
        myself.set_language('tr')
        self.window.retranslate_all()
        self.assertEqual(self.page.title.text(), 'Masaüstü Ortamları')
        self.assertEqual(self.page.selected_greeter(), 'ly')
        self.window.stacked_widget.setCurrentWidget(self.page)
        self.window.show()
        self.app.processEvents()
        self.assertEqual(self.page.next_btn.grab().toImage().pixelColor(12,12).name(), '#ffffff')


class DesktopSetupTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.base = Path(self.directory.name)
        self.target = self.base/'target'
        (self.target/'etc').mkdir(parents=True)
        (self.target/'etc/passwd').write_text('demo:x:1000:1000::/home/demo:/bin/bash\n')
        self.home = self.target/'home/demo'
        self.home.mkdir(parents=True)
        fallback = self.target/desktop_setup.DEFAULT_WALLPAPER.lstrip('/')
        fallback.parent.mkdir(parents=True)
        fallback.write_bytes(b'fixture')
        self.assets = self.base/'assets'
        self.assets.mkdir()
        (self.assets/'desktop_theme.py').write_text('# runtime\n')

    def tearDown(self):
        self.directory.cleanup()

    def test_all_desktops_have_distinct_configuration_and_fallback_wallpapers(self):
        defaults = {'etc/sway/config':'# sway bindings\n', 'etc/i3/config':'# i3 bindings\n',
                    'usr/share/hypr/hyprland.lua':'-- hypr bindings\n',
                    'usr/share/doc/bspwm/examples/bspwmrc':'#!/bin/sh\n# bspwm bindings\n'}
        for filename,text in defaults.items():
            p = self.target/filename
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        names = [d.name for d in DESKTOPS]
        wallpapers = desktop_setup.install_defaults(self.target, self.assets, names, 'sddm')
        self.assertEqual(set(wallpapers), {d.slug for d in DESKTOPS})
        self.assertTrue((self.home/'.config/hypr/zelix.lua').is_file())
        self.assertIn('hl.config', (self.home/'.config/hypr/zelix.lua').read_text())
        self.assertIn('# sway bindings', (self.home/'.config/sway/config').read_text())
        self.assertIn('client.focused', (self.home/'.config/i3/zelix.conf').read_text())
        self.assertIn('focused_border_color', (self.home/'.config/bspwm/bspwmrc').read_text())
        self.assertFalse((self.home/'.config/gtk-3.0/settings.ini').exists())
        initial = (self.home/'.config/hypr/hyprland.lua').read_text()
        desktop_setup.install_defaults(self.target, self.assets, names, 'sddm')
        self.assertEqual((self.home/'.config/hypr/hyprland.lua').read_text(), initial)

    def test_custom_wallpaper_only_applies_to_its_desktop(self):
        folder = self.assets/'backgrounds/gnome'
        folder.mkdir(parents=True)
        image = QImage(16,16,QImage.Format.Format_RGB32)
        image.fill(0x112233)
        image.save(str(folder/'wallpaper.png'))
        wallpapers = desktop_setup.install_defaults(self.target, self.assets, ['KDE Plasma','GNOME'], 'gdm')
        self.assertEqual(wallpapers['gnome'], '/usr/share/wallpapers/Zelix/gnome/wallpaper.png')
        self.assertEqual(wallpapers['kde-plasma'], desktop_setup.DEFAULT_WALLPAPER)
        self.assertEqual((self.target/wallpapers['gnome'].lstrip('/')).read_bytes(), (folder/'wallpaper.png').read_bytes())

    def test_kde_keeps_automatic_aurora_even_if_custom_file_is_present(self):
        folder = self.assets/'backgrounds/kde-plasma'
        folder.mkdir(parents=True)
        image = QImage(16,16,QImage.Format.Format_RGB32)
        image.fill(0xABCDEF)
        image.save(str(folder/'wallpaper.png'))
        wallpapers = desktop_setup.install_defaults(self.target, self.assets, ['KDE Plasma'], 'sddm')
        self.assertEqual(wallpapers['kde-plasma'], desktop_setup.DEFAULT_WALLPAPER)
        self.assertFalse((self.target/'usr/share/wallpapers/Zelix/kde-plasma').exists())

    def test_legacy_hyprland_config_is_preserved(self):
        config = self.home/'.config/hypr/hyprland.conf'
        config.parent.mkdir(parents=True)
        config.write_text('# existing bindings\n')
        desktop_setup.install_defaults(self.target,self.assets,['Hyprland'],'ly')
        self.assertIn('# existing bindings',config.read_text())
        self.assertTrue((config.parent/'zelix.conf').is_file())
        self.assertFalse((config.parent/'hyprland.lua').exists())

    def test_installed_sddm_does_not_inherit_live_autologin_or_wayland_backend(self):
        payload = ROOT/'zelixins/zelixdeps/etc'
        for filename in ('sddm.conf','sddm.conf.d/zelix.conf','sddm.conf.d/kde_settings.conf'):
            config = configparser.ConfigParser()
            config.read(payload/filename)
            self.assertFalse(config.has_section('Autologin'), filename)
            self.assertFalse(config.has_option('General','DisplayServer'), filename)
        live = configparser.ConfigParser()
        live.read(ROOT/'iso_root/airootfs/etc/sddm.conf')
        self.assertEqual(live['Autologin']['User'], 'zelix')

    def test_running_root_or_unsupported_greeter_is_rejected(self):
        with self.assertRaises(ValueError):
            desktop_setup.install_defaults('/', self.assets,['GNOME'],'gdm')
        with self.assertRaises(ValueError):
            desktop_setup.install_defaults(self.target,self.assets,['GNOME','Hyprland'],'gdm')


class InstalledDesktopParserTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('archinstall'), 'archinstall is not installed')
    def test_archinstall_parses_all_profiles_and_ly_tty_service(self):
        from archinstall.lib.profile.profiles_handler import profile_handler
        from archinstall.lib.models.profile import ProfileConfiguration
        from archinstall.lib.log import logger
        from archinstall.default_profiles.profile import GreeterType
        with tempfile.TemporaryDirectory() as directory, patch.object(logger, '_path', Path(directory)):
            profile = ProfileConfiguration.parse_arg({'profile': {
                'main': 'Desktop', 'details': [desktop.profile for desktop in DESKTOPS],
                'custom_settings': {'Hyprland': {'seat_access': 'systemd-logind'},
                                    'Sway': {'seat_access': 'systemd-logind'}}},
                'greeter': 'sddm', 'gfx_driver': None})
            self.assertEqual([p.name for p in profile.profile.current_selection],
                             [desktop.profile for desktop in DESKTOPS])
            fake_install = MagicMock()
            profile_handler.install_greeter(fake_install, GreeterType.Ly)
            fake_install.enable_service.assert_called_with(['ly@tty1'])
            fake_install.disable_service.assert_called_with(['getty@tty1'])

    @unittest.skipUnless(shutil.which('Hyprland') and Path('/usr/share/hypr/hyprland.lua').is_file(),
                         'Hyprland Lua verifier is not installed')
    def test_real_hyprland_parser_accepts_seeded_theme(self):
        with tempfile.TemporaryDirectory(prefix='zelix-hypr-test-') as directory:
            base = Path(directory)
            target, home = base/'target', base/'home'
            sample = target/'usr/share/hypr/hyprland.lua'
            sample.parent.mkdir(parents=True)
            sample.write_text(Path('/usr/share/hypr/hyprland.lua').read_text())
            desktop_setup.seed_window_manager(target, home, 'hyprland', '/usr/share/wallpapers/Zelix/hyprland/wallpaper.png')
            config = home/'.config/hypr/hyprland.lua'
            env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home/'.config'),
                       XDG_DATA_HOME=str(base/'data'), XDG_CACHE_HOME=str(base/'cache'),
                       XDG_STATE_HOME=str(base/'state'))
            result = subprocess.run(['Hyprland', '--verify-config', '-c', str(config)],
                                    env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)


class DesktopRuntimeTests(unittest.TestCase):
    def test_session_detection(self):
        self.assertEqual(desktop_theme.session_slug({'XDG_CURRENT_DESKTOP':'ubuntu:GNOME'}), 'gnome')
        self.assertEqual(desktop_theme.session_slug({'XDG_CURRENT_DESKTOP':'XFCE'}), 'xfce')
        self.assertIsNone(desktop_theme.session_slug({'XDG_CURRENT_DESKTOP':'KDE'}))

    def test_gnome_and_xfce_commands_do_not_touch_other_sessions(self):
        with patch.object(desktop_theme,'run',return_value='accent-color\n') as run:
            desktop_theme.apply('gnome','/usr/share/wallpapers/gnome.png')
            calls = [call.args[0] for call in run.call_args_list]
            self.assertTrue(all(command[0]=='gsettings' for command in calls))
            self.assertIn(['gsettings','set','org.gnome.desktop.interface','accent-color','slate'],calls)
        with patch.object(desktop_theme,'run',return_value='/backdrop/screen0/monitor0/workspace0/last-image'), \
             patch.object(desktop_theme,'xfconf_set') as setter:
            desktop_theme.apply('xfce','/usr/share/wallpapers/xfce.png')
            setter.assert_any_call('xsettings','/Net/ThemeName','Materia-dark')
            self.assertFalse(any('gnome' in str(call) for call in setter.call_args_list))

    def test_failure_retries_then_success_is_once_per_user(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            wallpaper = base/'wallpaper.png'
            wallpaper.touch()
            config = base/'desktops.json'
            config.write_text(json.dumps({'desktops':['gnome'], 'wallpapers':{'gnome':str(wallpaper)}}))
            env = dict(os.environ,XDG_CURRENT_DESKTOP='GNOME',XDG_STATE_HOME=str(base/'state'))
            marker = base/'state/zelix/appearance-gnome-v1.done'
            with patch.dict(os.environ,env,clear=True), patch.object(desktop_theme,'apply',side_effect=RuntimeError('not ready')):
                self.assertEqual(desktop_theme.initialize(config),1)
                self.assertFalse(marker.exists())
            with patch.dict(os.environ,env,clear=True), patch.object(desktop_theme,'apply') as apply:
                self.assertEqual(desktop_theme.initialize(config),0)
                self.assertTrue(marker.exists())
                self.assertEqual(desktop_theme.initialize(config),0)
                apply.assert_called_once()


if __name__ == '__main__':
    unittest.main()
