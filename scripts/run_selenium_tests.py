"""Run all Selenium test files together.

Start Odoo and activate the virtual environment with Selenium installed, then
run this from the project folder:
    python scripts/run_selenium_tests.py

Name each test file test_*.py (for example, test_login.py). Inside each file,
use unittest.TestCase classes with methods whose names start with test_.
New test files are picked up automatically; no changes to this wrapper are
needed. Each file can still be run on its own.
"""

from pathlib import Path
import sys
import unittest


def main():
    # Find the selenium folder relative to this script, so finding the tests
    # does not depend on which folder our terminal is currently in.
    project_folder = Path(__file__).resolve().parent.parent
    test_folder = project_folder / "selenium"

    # unittest imports the matching files and collects their test methods.
    # Importing them does not run their unittest.main() blocks, because those
    # blocks only run when a file is started directly with Python.
    suite = unittest.TestLoader().discover(str(test_folder), pattern="test_*.py")

    # Catch an empty folder or incorrectly named tests instead of reporting
    # a successful run when we have not actually checked anything.
    if suite.countTestCases() == 0:
        print(f"No tests found in {test_folder}. Name test files test_*.py.",
              file=sys.stderr)
        return 1

    # Run the collected tests one at a time.
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Zero tells the terminal everything passed. One means a test failed or
    # had an error.
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
