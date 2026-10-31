import importlib.util
from pathlib import Path
import sys
import unittest


spec = importlib.util.spec_from_file_location(
    'run_team_tests', Path(__file__).resolve().parents[1] / 'run_team_tests.py',
)
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


def log(logger, message):
    return f'2026-10-31 02:04:37,127 1 INFO test_db {logger}: {message}\n'


class TestTeamReport(unittest.TestCase):
    def test_duplicate_class_names_and_printed_output_stay_separate(self):
        output = (
            log('odoo.addons.fleet.tests.test_one', 'Starting TestFleet.test_one ... ')
            + 'printed by first test\n'
            + log('odoo.modules.loading', 'Module fleet loaded')
            + log('odoo.modules.loading', 'Loading hospital')
            + log('odoo.addons.om_hospital.tests.test_two', 'Starting TestFleet.test_two ... ')
            + 'printed by second test\n'
            + log('odoo.addons.om_hospital.tests.test_two', 'FAIL: TestFleet.test_two')
            + 'Traceback\nAssertionError: failed assertion\n'
            + log('odoo.tests.result', "1 failed, 0 error(s) of 2 tests when loading database 'test_db'")
        )
        cases, _ = runner.parse_output(output)
        self.assertEqual([case.status for case in cases], ['PASS', 'FAIL'])
        self.assertIn('fleet.tests.test_one.', cases[0].name)
        self.assertIn('printed by first test', '\n'.join(cases[0].output))
        self.assertNotIn('Loading hospital', '\n'.join(cases[0].output))
        self.assertNotIn('printed by first test', '\n'.join(cases[1].output))
        self.assertIn('AssertionError: failed assertion', '\n'.join(cases[1].output))

    def test_interrupted_test_is_not_reported_as_pass(self):
        output = log('odoo.addons.fleet.tests.test_one', 'Starting TestFleet.test_one ...')
        cases, _ = runner.parse_output(output)
        self.assertEqual(cases[0].status, 'INCOMPLETE')
        report, completed = runner.format_report(output, 'test_db', 137, 'full.log')
        self.assertFalse(completed)
        self.assertIn('did not finish normally', report)

    def test_skip_and_class_setup_error_are_reported(self):
        logger = 'odoo.addons.fleet.tests.test_one'
        output = (
            log(logger, 'Starting TestFleet.test_one ...')
            + log(logger, 'skipped TestFleet.test_one : unavailable feature')
            + log('odoo.modules.loading', 'Module fleet loaded')
            + log(logger, 'ERROR: setUpClass (TestAnotherClass)')
            + 'RuntimeError: setup failed\n'
            + log('odoo.tests.result', "0 failed, 1 error(s) of 1 tests when loading database 'test_db'")
        )
        cases, _ = runner.parse_output(output)
        self.assertEqual([case.status for case in cases], ['SKIP', 'ERROR'])
        report, _ = runner.format_report(output, 'test_db', 1, 'full.log')
        self.assertIn('setup failed', report)
        self.assertIn('Odoo totals differ', report)

    def test_zero_tests_is_not_a_successful_run(self):
        output = log('odoo.tests.result', "0 failed, 0 error(s) of 0 tests when loading database 'test_db'")
        _, completed = runner.format_report(output, 'test_db', 0, 'full.log')
        self.assertFalse(completed)

    def test_failed_subtest_marks_its_parent_test_as_failed(self):
        logger = 'odoo.addons.fleet.tests.test_one'
        output = (
            log(logger, 'Starting TestFleet.test_one ...')
            + log(logger, 'FAIL: Subtest TestFleet.test_one (reading=1000)')
            + 'AssertionError: wrong reading\n'
            + log('odoo.tests.result', "1 failed, 0 error(s) of 1 tests when loading database 'test_db'")
        )
        cases, _ = runner.parse_output(output)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].status, 'FAIL')
