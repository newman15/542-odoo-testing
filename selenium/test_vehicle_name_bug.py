"""Negative: fleet vehicle name should be Brand/Model/License Plate

Fleet builds vehicle name in _computer_vehicle_name (fleet_vehicle.py).
On this branch where that method has the intentional bug, the name is wrong
and this test fails.
"""

import time
import unittest
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://localhost:8069"
DATABASE = "odoo18"
USERNAME = "admin@example.com"
PASSWORD = "admin"
WAIT_SECONDS = 20

# The model we pick in the form and how it appears in Odoo's dropdown
MODEL_SEARCH_TEXT = "A1"
MODEL_DROPDOWN_TEXT = "Audi/A1"

class TestFleetVehicleName(unittest.TestCase):
    """Create a vehicle in the browser and check the name Odoo gives it."""

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, WAIT_SECONDS)

    def log_in(self):
        """Sign in the same way test_login.py does."""
        driver = self.driver
        driver.get(f"{BASE_URL}/web/login?{urlencode({'db': DATABASE})}")

        login_box = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "login"))
        )
        password_box = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        login_box.clear()
        login_box.send_keys(USERNAME)
        password_box.clear()
        password_box.send_keys(PASSWORD)

        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "form.oe_login_form button[type='submit']")
            )
        ).click()

        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".o_user_menu")),
            message="Login failed. Check the database and account settings.",
        )

    def test_vehicle_name_shows_brand_model_plate(self):
        """A new vehicle should be named Brand/Model/License Plate."""
        driver = self.driver
        self.log_in()

        # A unique plate lets us find our own vehicle even after repeated runs.
        plate = f"SEL-{int(time.time()) % 100000}"
        expected_name = f"Audi/A1/{plate}"

        # Open a new vehicle form directly.
        driver.get(f"{BASE_URL}/odoo/action-fleet.fleet_vehicle_action/new")

        # Pick the model from the autocomplete dropdown.
        model_input = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[name='model_id'] input")
            )
        )
        model_input.click()
        model_input.send_keys(MODEL_SEARCH_TEXT)

        model_option = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[contains(@class, 'o-autocomplete--dropdown-item')]"
                    f"//*[normalize-space(text())='{MODEL_DROPDOWN_TEXT}']",
                )
            ),
            message="Could not find the Audi/A1 model in the dropdown.",
        )
        model_option.click()

        # Type the license plate.
        plate_input = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[name='license_plate'] input")
            )
        )
        plate_input.clear()
        plate_input.send_keys(plate)

        # Save the record.
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".o_form_button_save")
            )
        ).click()

        # After saving, Odoo shows the record's name in the breadcrumb.
        # Wait until our plate appears there, then read the full name.
        breadcrumb = (By.CSS_SELECTOR, ".o_breadcrumb .active")
        self.wait.until(
            EC.text_to_be_present_in_element(breadcrumb, plate),
            message="The saved vehicle name never showed our license plate.",
        )
        actual_name = driver.find_element(*breadcrumb).text.strip()

        # Clean source gives "Audi/A1/<plate>". The injected bug does not.
        self.assertEqual(
            actual_name,
            expected_name,
            f"Vehicle name should be '{expected_name}' but was '{actual_name}'.",
        )

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)