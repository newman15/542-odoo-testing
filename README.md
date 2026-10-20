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

## 8. Normal Development Workflow

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

## 9. Completely Reset the Environment

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

## 10. Working With Fleet Source

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

## 11. Known om_hospital Behavior

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