"""Run all Fleet and Hospital tests and report their output by test case."""

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys


# Odoo prefixes log messages with time, process ID, level, database and logger.
# Named regex groups let us read the logger/message without slicing that prefix.
LOG_LINE = re.compile(
    r'^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d+ \d+ '
    r'(?P<level>\w+) \S+ (?P<logger>[^:]+): (?P<message>.*)$'
)
# Use Odoo's final totals as a check that the test run reached its conclusion.
SUMMARY = re.compile(
    r'(\d+) failed, (\d+) error\(s\) of (\d+) tests when loading database [^\n]+'
)


@dataclass
class TestOutput:
    # One report block per test method. default_factory gives each test its own
    # output list instead of sharing a mutable list between tests.
    name: str
    status: str = 'PASS'
    output: list = field(default_factory=list)


def parse_output(output):
    """Keep test logs/tracebacks together, using Odoo's test-start markers."""
    cases = []
    current = None
    for line in output.splitlines():
        entry = LOG_LINE.match(line)
        if entry:
            logger, message = entry['logger'], entry['message'].rstrip()
            is_test = logger.startswith(('odoo.addons.fleet.tests.',
                                         'odoo.addons.om_hospital.tests.'))
            if is_test and message.startswith('Starting ') and message.endswith(' ...'):
                # Keep the module path: different files can use the same class name.
                current = TestOutput(f'{logger.removeprefix("odoo.addons.")}.{message[9:-4]}')
                cases.append(current)
                continue
            # Module loading resumes after a module's tests finish. Do not
            # attach the next module's startup warnings to the preceding test.
            if logger in ('odoo.modules.loading', 'odoo.modules.registry',
                          'odoo.service.server', 'odoo.tests.stats', 'odoo.tests.result'):
                current = None
                continue
            failure = re.match(r'(FAIL|ERROR): (.+)', message) if is_test else None
            if failure:
                # A failing subTest belongs to its parent method, not a new test.
                description = failure[2].removeprefix('Subtest ')
                name = f'{logger.removeprefix("odoo.addons.")}.{description}'
                # setUpClass/tearDownClass failures can occur without startTest.
                if current is None or not name.startswith(current.name):
                    current = TestOutput(name)
                    cases.append(current)
                if current.status != 'ERROR':
                    current.status = failure[1]
            if current and is_test and message.startswith('skipped '):
                current.status = 'SKIP'
            if current and message.strip() and set(message.strip()) == {'='}:
                continue
        # print() output and traceback lines have no Odoo prefix. Keep those too,
        # along with logs from models called while the test is running.
        if current:
            current.output.append(line)

    summaries = list(SUMMARY.finditer(output))
    summary = summaries[-1] if summaries else None
    if summary is None:
        # A process crash provides no authoritative success result.
        for case in cases:
            if case.status == 'PASS':
                case.status = 'INCOMPLETE'
    return cases, summary


def format_report(output, database, returncode, log_path):
    # Build one string for both terminal output and the saved text report.
    cases, summary = parse_output(output)
    lines = [f'Team tests: {database}', '']
    for case in cases:
        lines.extend(['=' * 78, f'{case.status}  {case.name}', '-' * 78])
        captured = '\n'.join(case.output).strip()
        lines.extend([captured or '(No test output.)', ''])

    counts = Counter(case.status for case in cases)
    lines.extend(['=' * 78, 'SUMMARY'])
    lines.append(', '.join(f'{count} {status}' for status, count in sorted(counts.items()))
                 or 'No test cases detected.')
    if summary:
        lines.append(summary[0])
        # Setup/teardown failures may create extra blocks without running a method.
        if int(summary[3]) != len(cases):
            lines.append('Odoo totals differ from the case list; inspect the full log '
                         'for suite setup/teardown failures or discovery issues.')
    else:
        lines.extend(['No final Odoo result; the run did not finish normally.',
                      '', 'Last log lines:', *output.splitlines()[-15:]])
    lines.extend([f'Exit status: {returncode}', f'Full log: {log_path}'])
    # A clean exit with zero discovered tests should not count as a usable run.
    return '\n'.join(lines) + '\n', bool(summary and int(summary[3]) > 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default='odoo18_test_cases')
    parser.add_argument('--install', action='store_true',
                        help='Install addons on the first run instead of updating them.')
    args = parser.parse_args()
    # Resolve paths from this script, so reports always land in the repo root.
    root = Path(__file__).resolve().parent.parent
    # Pass arguments as a list, without a shell. -T disables the interactive
    # terminal; unbuffered Python keeps print() output in order with Odoo logs.
    command = [
        'docker', 'compose', 'run', '--rm', '-T',
        '-e', 'PYTHONUNBUFFERED=1', 'odoo', 'odoo',
        '-d', args.database,
        '--db_host=db', '--db_port=5432', '--db_user=odoo', '--db_password=odoo',
        '-i' if args.install else '-u', 'om_hospital,fleet',
        '--test-tags',
        # Select whole addons so new registered test classes are included.
        '/om_hospital,/fleet',
        '--stop-after-init', '--http-port=8070',
    ]
    if args.install:
        command.append('--without-demo=all')

    # Keep the original log as well as the readable report. Include microseconds
    # and the local UTC offset in names to distinguish runs and identify the time.
    reports = root / 'reports'
    reports.mkdir(exist_ok=True)
    run_name = datetime.now().astimezone().strftime('team-tests-%Y%m%d-%H%M%S-%f%z')
    log_path = reports / f'{run_name}.log'
    report_path = reports / f'{run_name}.txt'
    with log_path.open('w') as log:
        print(f'Running team tests on {args.database}...', flush=True)
        print(f'Full log: {log_path}', flush=True)
        try:
            # Wait for Docker, saving stdout and stderr in the same log. check=False
            # lets us generate the report even when a failed test returns nonzero.
            result = subprocess.run(command, cwd=root, stdout=log,
                                    stderr=subprocess.STDOUT, check=False)
        except OSError as error:
            message = f'Could not launch Docker: {error}\n'
            log.write(message)
            report_path.write_text(message)
            print(message, file=sys.stderr, end='')
            print(f'Report: {report_path}')
            return 1

    report, completed = format_report(
        log_path.read_text(errors='replace'), args.database, result.returncode, log_path,
    )
    report_path.write_text(report)
    print(f'\n{report}', end='')
    print(f'Report: {report_path}')
    # Preserve failures for shell scripts/CI, and also fail an unfinished run.
    return result.returncode if completed else (result.returncode or 1)


if __name__ == '__main__':
    sys.exit(main())
