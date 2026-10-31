# 542 Odoo Testing Project

Development and testing environment for the group Odoo project.

The project uses Docker to provide a consistent Odoo environment across macOS, Windows, and Linux without requiring Odoo or PostgreSQL to be installed directly on each group member's computer.

## Environment

- Odoo 18 Community
- PostgreSQL 15
- Docker / Docker Compose
- Python 3.12 inside the Odoo container
- Odoo Python unit testing
- Selenium testing
- VS Code Dev Containers support

The two applications under test are:

- `om_hospital`, originally an Odoo 15 module provided for the course and ported to Odoo 18.
- `fleet`, the official Odoo Fleet application. The Odoo 18 source is included in this repository so that tests and intentional defects can be version controlled.

## Repository Structure

```text
542-odoo-testing/
├── .devcontainer/
│   └── devcontainer.json
│
├── addons/
│   ├── om_hospital/
│   │   ├── models/
│   │   ├── tests/
│   │   ├── views/
│   │   └── ...
│   │
│   └── fleet/
│       ├── models/
│       ├── tests/
│       ├── views/
│       └── ...
│
├── .gitignore
├── compose.yaml
└── README.md
```

## Prerequisites

Install the following before starting:

- Git
- Docker Desktop or Docker Engine with Docker Compose
- VS Code, recommended
- VS Code Dev Containers extension, recommended

Docker Desktop:

https://www.docker.com/products/docker-desktop/

VS Code Dev Containers:

https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers

Odoo and PostgreSQL do **not** need to be installed directly on the host computer.

## 1. Clone the Repository

```bash
git clone git@github.com:newman15/542-odoo-testing.git
cd 542-odoo-testing
```

If SSH access to GitHub has not been configured, clone using the repository's HTTPS URL instead.

## 2. Start the Environment

Make sure Docker Desktop or Docker Engine is running.

Pull the required images:

```bash
docker compose pull
```

Start Odoo and PostgreSQL:

```bash
docker compose up -d
```

The `-d` option runs the containers in the background.

Verify that both containers are running:

```bash
docker compose ps
```

You should see both the `db` and `odoo` services running.

Odoo will be available at:

```text
http://localhost:8069
```

## 3. Create the Odoo Database

The first time the environment is started, open:

```text
http://localhost:8069
```

Odoo will display its initial database setup page.

For consistency between group members, use:

```text
Master Password: admin
Database Name:   odoo18
Email:           admin@example.com
Password:        admin
Phone:           <blank>
Language:        English
Country:         United States
Demo Data:       ✓
```

Demo data may be enabled if desired.

These credentials are intended only for this local classroom development environment.

Each group member has their **own local PostgreSQL database**. Database contents, users, passwords, test records, and installed application state are not stored in Git.

## 4. Install om_hospital

The `om_hospital` source is already included under:

```text
addons/om_hospital
```

The repository version has been updated for compatibility with Odoo 18.

In Odoo:

1. Open **Apps**.
2. Enable Developer Mode.
3. Select **Update Apps List**.
4. Locate the om_hospital module, its name as "Odoo 15 Development Tutorials".
5. Select **Activate**.

After installation, verify that the Hospital application opens.

You should be able to work with:

- Patients
- Doctors
- Appointments

## 5. Install Fleet

Fleet is included with Odoo 18.

From **Apps**, locate:

```text
Fleet
```

and select **Activate**.

The repository also contains a copy of the matching Odoo 18 Fleet source:

```text
addons/fleet
```

Docker mounts this directory over the Fleet source inside the Odoo container:

```text
./addons/fleet
        ↓
/usr/lib/python3/dist-packages/odoo/addons/fleet
```

This allows our group to version-control Fleet tests and any intentional source changes used for negative testing.

## 6. VS Code Development Environment

Using the Dev Container is recommended because Odoo and its Python dependencies exist inside the Docker container rather than on the host computer.

Without the Dev Container, VS Code may report errors such as:

```text
Import "odoo.tests.common" could not be resolved
```

even though the code works correctly inside Odoo.

### Open the Dev Container

Open the repository in VS Code.

Open the Command Palette:

```text
Cmd+Shift+P
```

on macOS or:

```text
Ctrl+Shift+P
```

on Windows/Linux.

Select:

```text
Dev Containers: Reopen in Container
```

VS Code will connect to the Odoo development environment.

The development workspace is:

```text
/mnt/extra-addons
```

and should contain:

```text
fleet/
om_hospital/
```

The Dev Container automatically configures:

- Python
- Pylance
- Odoo-aware Python imports
- Bash as the integrated terminal

Verify Python:

```bash
python3 --version
```

Verify Odoo is available:

```bash
python3 -c "import odoo; print(odoo.__file__)"
```

## 7. Running the Hospital Unit Tests

Hospital tests are stored under:

```text
addons/om_hospital/tests/
```

A basic smoke test is included to verify that the Odoo testing framework is working.

From the host terminal, run:

```bash
docker compose run --rm odoo \
  odoo \
  -d odoo18 \
  --db_host=db \
  --db_port=5432 \
  --db_user=odoo \
  --db_password=odoo \
  -u om_hospital \
  --test-tags /om_hospital:TestHospitalSmoke \
  --stop-after-init \
  --http-port=8070
```

A successful run should report:

```text
0 failed, 0 error(s)
```

The temporary Odoo container automatically exits after the test completes.

The normal Odoo web application remains available on port `8069`.

### Test Data

Unit tests should create the records they require rather than relying on records manually created through the Odoo interface.

For example, tests should create their own patients, doctors, vehicles, or appointments.

This keeps tests consistent between group members even though each person has a different local database.

## 8. Running Team Tests

Run these commands from the repository root in a host terminal with Docker
running. Team tests are stored in `addons/om_hospital/tests/` and
`addons/fleet/tests/`.

### Test cases

Two additional test cases are available:

- `TestHospitalAppointmentMissingDoctor`: temporarily removes doctor ID `2`
  inside the test transaction and invokes the Create Appointment wizard.
  Existing appointments are temporarily reassigned if necessary. This test is
  intentionally expected to **fail** while the wizard hard-codes `doctor_id=2`.
  Test rollback restores the existing records; do not manually delete a doctor
  or reset the development database for this test.
- `TestFleetOdometer`: increases a vehicle's odometer from `1,000` to `1,250`
  kilometers and verifies the current reading and both history entries.

### Testing approach

These are Python tests run by Odoo inside Docker. They call model and wizard
methods through Odoo's ORM (its database API), so they exercise application
logic against PostgreSQL. They do not open a browser or test page layout;
Selenium testing is a separate part of the project.

Each of our two tests inherits from `TransactionCase`, which provides
`self.env` for accessing models and rolls back record changes after the test.
They create their own data and check results with assertions. Fleet checks
both the computed odometer reading and the saved history. Hospital calls the
Create Appointment wizard with doctor `2` absent, catches that specific
foreign-key violation inside a savepoint, and reports an explicit failure.
The savepoint allows database cleanup to proceed after the SQL error. This
test demonstrates the known bug; it does not fix the wizard.

To add coverage, create a `test_*.py` file under the appropriate addon's
`tests/` directory, import it in `tests/__init__.py`, and add a `TransactionCase`
class with methods named `test_*`. Create valid test records rather than
assuming demo records or particular IDs exist. Hospital's ID `2` is an
intentional exception because that exact value triggers the defect.

### Readable results (recommended)

With Python 3.9 or later installed on the host, run:

```bash
python3 scripts/run_team_tests.py
```

The runner uses `odoo18_test_cases` and selects **all registered tests** in
`om_hospital` and `fleet`, including the existing smoke and Fleet tests. New
test files must be imported in their addon's `tests/__init__.py`; new classes
and methods then run without editing the runner.

After Docker finishes, the terminal displays a separate block for every test
method, with its result, printed output, log messages, and any traceback.
Test names include their addon and file so similarly named classes remain
distinct. The final summary lists the totals. Tests that are skipped or whose
run is interrupted are identified separately.

The runner groups Odoo's log using its test-start and result messages; it does
not execute the test methods itself. A test with no failure or skip message
is reported as passing only when Odoo also supplies a final run summary.
If the number of report blocks differs from Odoo's total, inspect the full log
for setup/teardown failures. Output outside a test block, including addon
startup messages, remains available in that log.

Each run creates two timestamped files in `reports/` at the repository root:

- `team-tests-<timestamp>.txt`: the same grouped report displayed in the terminal.
- `team-tests-<timestamp>.log`: all Docker/Odoo output, including startup and
  module update messages omitted from the grouped report.

Both paths are printed. The `reports/` folder is gitignored and persists until
you remove it. The runner preserves the command's nonzero exit status when a
test fails. If startup fails before tests finish, the report includes the last
log lines instead of claiming the tests passed.

For the first run on a database without these addons installed:

```bash
python3 scripts/run_team_tests.py --install
```

To select another database, add `--database YOUR_DATABASE_NAME`.
The full Docker commands and their options are documented below.

### First run: initialize a separate test database

The recommended database is `odoo18_test_cases`, separate from the development
database `odoo18`. If the test database does not exist yet, this command creates
it and installs both addons and their dependencies:

```bash
docker compose run --rm odoo odoo \
  -d odoo18_test_cases \
  --db_host=db --db_port=5432 --db_user=odoo --db_password=odoo \
  -i om_hospital,fleet --without-demo=all \
  --test-tags /om_hospital,/fleet \
  --stop-after-init --http-port=8070
```

### Subsequent runs: reuse the test database

Once both addons are installed, use `-u` to update them and run the tests again:

```bash
docker compose run --rm odoo odoo \
  -d odoo18_test_cases \
  --db_host=db --db_port=5432 --db_user=odoo --db_password=odoo \
  -u om_hospital,fleet \
  --test-tags /om_hospital,/fleet \
  --stop-after-init --http-port=8070
```

With the current Hospital defect, expect the missing-doctor test to fail and
a nonzero exit status. The remaining tests should pass. The Hospital test
expects appointment creation to succeed, so reproducing the foreign-key error
reports a failure. The last verified full run had **5 passing tests, 1 failing
test, and 0 errors**; this total will change as tests are added.

### Command options

| Option | Meaning |
| --- | --- |
| `docker compose run --rm odoo` | Create a temporary container using the `odoo` service configuration and remove it when the command exits. Start the database dependency if needed. |
| Second `odoo` in the command | Run the Odoo executable inside that temporary container. |
| `-d odoo18_test_cases` | Select the database to use. It is reused on later runs; this does not request a fresh database every time. |
| `-i om_hospital,fleet` | Install the named addons into the selected database. Use this when they are not installed yet. |
| `-u om_hospital,fleet` | Update the already-installed addons in the selected database. Use this for subsequent test runs. |
| `--without-demo=all` | Skip demo data when initializing the database and installing addons. Our tests supply their own records. |
| `--test-tags /om_hospital,/fleet` | Enable tests and select both addons' registered tests. Commas separate selections; adding `:ClassName` selects one class. |
| `--db_host=db` | Connect to the PostgreSQL service named `db` on the Compose network. |
| `--db_port=5432` | Use PostgreSQL's port inside the Compose network. |
| `--db_user=odoo` / `--db_password=odoo` | Use the local development database credentials configured in `compose.yaml`. |
| `--stop-after-init` | Exit Odoo after module loading and the selected tests finish. |
| `--http-port=8070` | Set the test process's HTTP port inside its container. `compose run` does not publish service ports by default. |

To run just one team test class, use either
`--test-tags /fleet:TestFleetOdometer` or
`--test-tags /om_hospital:TestHospitalAppointmentMissingDoctor` in the direct
Docker command. The Python runner always selects both entire addons.

### Container and database persistence

The temporary Odoo container connects to PostgreSQL; it does not contain the
test database:

```text
Temporary Odoo test container
            | connects to
PostgreSQL service (db)
            | stores database files in
Persistent Docker volume (odoo-db-data)
```

After a run, `--rm` removes only the temporary Odoo container. The database and
installed addons remain available for the next run. These `TransactionCase`
tests roll back their record changes, including Hospital's temporary doctor
deletion and appointment reassignment. Module installation and updates persist.

`docker compose down` preserves the database volume. `docker compose down -v`
deletes the volumes, including **all development and test databases** stored
there. No database reset is needed to rerun the tests.

### Using an existing development database

Tests can also run against an existing database: replace
`-d odoo18_test_cases` with `-d odoo18` (or your database's actual name).
Use `-i` for addons not installed in that database and `-u` for addons already
installed. If their installation states differ, use, for example,
`-i om_hospital -u fleet` when only Fleet is already installed.

Addon installation is specific to each database. The source code makes an addon
available to Odoo, but it must be installed in the selected database before its
tests can run. The first-run command performs that installation without using
the Apps interface. Installing Hospital in `odoo18_test_cases` does not install
it in `odoo18`.

Prefer the separate test database because installation and updates change the
selected database even though the test methods roll back their record changes.
The normal Odoo web container remains separate and available on port `8069`.

## 9. Normal Development Workflow

Start the environment:

```bash
docker compose up -d
```

Check status:

```bash
docker compose ps
```

View Odoo logs:

```bash
docker compose logs -f odoo
```

Press `Ctrl+C` to stop following the logs. This does not stop Odoo.

Restart Odoo after Python source changes when necessary:

```bash
docker compose restart odoo
```

Stop the environment:

```bash
docker compose down
```

Normal `docker compose down` does **not** delete the Odoo database.

Start it again with:

```bash
docker compose up -d
```

and existing database contents should remain available.

## 10. Completely Reset the Environment

To destroy the containers **and all local Odoo/PostgreSQL data**, run:

```bash
docker compose down -v
```

**Warning:** `-v` deletes the Docker volumes containing the local database.

The next:

```bash
docker compose up -d
```

will create a completely fresh environment and the Odoo database setup page will appear again.

Source code is unaffected because it remains in Git.

## 11. Working With Fleet Source

Do not modify Fleet directly inside the disposable container filesystem.

The Git-controlled source is:

```text
addons/fleet
```

Docker maps that source into Odoo's built-in Fleet location.

Therefore changes made to:

```text
addons/fleet/
```

persist across container destruction and can be committed to Git.

This is especially useful for negative testing where an intentional defect may need to be introduced into Fleet.

A recommended workflow is to create a branch:

```bash
git switch -c demo/fleet-negative-test
```

Introduce the intentional defect, restart Odoo if necessary, and run the appropriate tests.

The changes can be reviewed with:

```bash
git diff
```

and discarded or isolated from the main branch when the demonstration is complete.

## 12. Known om_hospital Behavior

The original `om_hospital` module contains a Create Appointment wizard that hard-codes:

```python
'doctor_id': 2
```

If a doctor with database ID `2` does not exist, this workflow causes a database foreign-key constraint error.

This behavior is part of the original training module and has intentionally not been corrected.

It may be useful as a negative unit or Selenium test case.

## Useful Docker Commands

Start:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

Status:

```bash
docker compose ps
```

Odoo logs:

```bash
docker compose logs -f odoo
```

Restart Odoo:

```bash
docker compose restart odoo
```

Open a Bash shell inside Odoo:

```bash
docker compose exec odoo bash
```

List custom addons:

```bash
docker compose exec odoo ls -la /mnt/extra-addons
```

Completely reset the environment:

```bash
docker compose down -v
```

## Project Testing Requirements

The group project requires Python unit tests for:

```text
om_hospital: 5 test cases
fleet:       5 test cases
```

for a total of at least:

```text
10 Python unit tests
```

The project also requires Selenium browser testing against Odoo.

The current repository provides the reproducible Odoo environment and source-controlled applications needed to develop both portions of the project.
