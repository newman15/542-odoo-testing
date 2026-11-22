"""Create a Hospital patient and confirm it appears in the Patients list.

Run from the project folder with Odoo running and om_hospital installed:
    python selenium/test_create_patient.py

The test creates a uniquely named patient in the configured database. The
record remains there after the test so the test does not risk deleting a
different user's data. Use a separate test database or remove the marked
test patient manually when you no longer need it.
"""

import unittest
from datetime import datetime
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Update these values if your local Odoo database or account differs.
BASE_URL = "http://localhost:8069"
DATABASE = "odoo18"
USERNAME = "admin@example.com"
PASSWORD = "admin"
WAIT_SECONDS = 20


class TestCreateHospitalPatient(unittest.TestCase):
    """Check the patient creation workflow through Odoo's browser interface."""

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, WAIT_SECONDS)

    def test_created_patient_appears_in_patients_list(self):
        driver = self.driver

        # Sign in to the selected database.
        login_url = f"{BASE_URL}/web/login?{urlencode({'db': DATABASE})}"
        driver.get(login_url)
        self.wait.until(EC.visibility_of_element_located((By.NAME, "login"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "form.oe_login_form button[type='submit']")
            )
        ).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".o_user_menu")))

        # Open Odoo's app launcher (the grid icon), then choose Hospital.
        app_launcher = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//i[contains(@class, 'oi-apps')]]")
            )
        )
        app_launcher.click()

        # Open the Hospital application, then its Patients menu entry.
        hospital_app = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(concat(' ', normalize-space(@class), ' '), ' o_app ') and contains(., 'Hospital')]")
            )
        )
        hospital_app.click()

        # The module has a Patients parent menu and a Patients action menu.
        # Choose the visible matching entry; Odoo may render both levels.
        self.wait.until(
            lambda browser: any(
                item.is_displayed()
                for item in browser.find_elements(
                    By.XPATH,
                    "//*[self::a or self::button][normalize-space(.)='Patients']",
                )
            )
        )
        patient_menu_items = [
            item
            for item in driver.find_elements(
                By.XPATH,
                "//*[self::a or self::button][normalize-space(.)='Patients']",
            )
            if item.is_displayed()
        ]
        patient_menu_items[-1].click()

        # Start a new patient form and fill the required name plus a valid age.
        add_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.o_list_button_add"))
        )
        add_button.click()

        patient_name = "Selenium Test Patient " + datetime.now().strftime("%Y%m%d%H%M%S%f")
        name_field = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[name='name'] input.o_input")
            )
        )
        name_field.send_keys(patient_name)
        age_field = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[name='age'] input.o_input")
            )
        )
        age_field.send_keys("30")

        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.o_form_button_save"))
        ).click()

        # Check the saved record in the list, not just that Save was clicked.
        patient_row = self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//tr[contains(@class, 'o_data_row') and .//*[normalize-space()={patient_name!r}]]",
                )
            ),
            message=f"The saved patient {patient_name!r} did not appear in the Patients list.",
        )
        self.assertIn(patient_name, patient_row.text)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
