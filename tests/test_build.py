import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_pacman', ROOT/'scripts/prepare-pacman.py')
pacman = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pacman)


class PacmanConfigurationTests(unittest.TestCase):
    def test_relocated_checkout_gets_local_server_first(self):
        text = '[core]\nInclude = mirrors\n[zelixrepo]\nSigLevel = Optional TrustAll\nServer = https://example.org/stable\n'
        with tempfile.TemporaryDirectory(prefix='zelix-relocated-') as directory:
            rendered = pacman.render(text, Path(directory)/'ZelixRepo')
            expected = 'Server = file://' + directory + '/ZelixRepo'
            self.assertIn(expected, rendered)
            self.assertLess(rendered.index(expected), rendered.index('Server = https://'))
            self.assertIn('SigLevel = Optional TrustAll', rendered)
            self.assertNotIn('file://', text)

    def test_missing_or_duplicate_repository_is_rejected(self):
        for text in ('[core]\n', '[zelixrepo]\n[zelixrepo]\n'):
            with self.assertRaises(ValueError):
                pacman.render(text, '/tmp/repository')

    def test_whitespace_path_has_actionable_error(self):
        with self.assertRaisesRegex(ValueError, 'whitespace'):
            pacman.render('[zelixrepo]\n', '/tmp/path with spaces/ZelixRepo')

    def test_cli_does_not_mutate_profile(self):
        with tempfile.TemporaryDirectory(prefix='zelix-pacman-') as directory:
            base = Path(directory)
            profile = base/'pacman.conf'
            original = '[zelixrepo]\nServer = https://example.org/stable\n'
            profile.write_text(original)
            repository = base/'ZelixRepo'
            repository.mkdir()
            (repository/'zelixrepo.db').write_bytes(b'fixture')
            output = base/'build.conf'
            subprocess.run([sys.executable, str(ROOT/'scripts/prepare-pacman.py'),
                            str(profile), str(repository), str(output)], check=True)
            self.assertEqual(profile.read_text(), original)
            self.assertIn(str(repository), output.read_text())

    def test_shell_scripts_parse(self):
        for name in ('build.sh', 'build-packages.sh'):
            subprocess.run(['bash', '-n', str(ROOT/'scripts'/name)], check=True)


if __name__ == '__main__':
    unittest.main()
