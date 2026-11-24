import importlib.util
import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWidgets import QApplication

spec = importlib.util.spec_from_file_location('updater', Path(__file__).resolve().parents[1] / 'zelix-updater/main.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdaterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = updater.UpdaterWindow()

    def tearDown(self):
        self.window.close()

    def run_check(self, stdout, stderr, exit_code):
        script = 'import sys; sys.stdout.write(%r); sys.stderr.write(%r); sys.exit(%d)' % (stdout, stderr, exit_code)
        self.window.run_process('check', sys.executable, ['-c', script])
        loop = QEventLoop()
        self.window.process.finished.connect(loop.quit)
        QTimer.singleShot(5000, loop.quit)
        loop.exec()
        self.assertIsNone(self.window.operation)

    def test_available_packages_enable_update(self):
        self.run_check('linux 1 -> 2\nfoo 1 -> 2\n', '', 0)
        self.assertEqual(len(self.window.packages), 2)
        self.assertTrue(self.window.update_button.isEnabled())
        self.assertIn('linux 1 -> 2', self.window.log_view.toPlainText())

    def test_no_updates_is_not_an_error(self):
        self.run_check('', '', 2)
        self.assertEqual(self.window.t('no_updates'), self.window.status_label.text())
        self.assertFalse(self.window.update_button.isEnabled())

    def test_check_failure_does_not_enable_update(self):
        self.run_check('', 'database error', 1)
        self.assertEqual(self.window.t('check_failed'), self.window.status_label.text())
        self.assertIn('database error', self.window.log_view.toPlainText())
        self.assertFalse(self.window.update_button.isEnabled())


if __name__ == '__main__':
    unittest.main()
