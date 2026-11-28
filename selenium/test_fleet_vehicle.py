import unittest
from urllib.parse import urlencode
from uuid import uuid4

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Copy these four values from your working selenium/test_login.py file.
BASE_URL = "http://localhost:8069"
DATABASE = "odoo18"
USERNAME = "admin@example.com"
PASSWORD = "admin"  # Local classroom account only.
WAIT_SECONDS = 20


class TestFleetVehiclePositive(unittest.TestCase):
    """Valid vehicle details should be saved and survive a page reload."""

    def setUp(self):
        self.driver = webdriver.Chrome()
        # Close Chrome even when a later setup step or the test fails.
        self.addCleanup(self.driver.quit)
        self.driver.set_window_size(1440, 1000)
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, WAIT_SECONDS)

    def vehicle_input(self, field_name):
        """Locate a visible input by its field name in the Fleet form."""
        return self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f".o_form_view .o_field_widget[name='{field_name}'] input",
                )
            ),
            message=f"The vehicle '{field_name}' input did not appear.",
        )

    def test_create_vehicle_with_valid_details(self):
        """An existing model, license plate, and location can be saved."""
        driver = self.driver
        database_query = urlencode({"db": DATABASE})
        license_plate = f"SEL-{uuid4().hex[:12].upper()}"
        location = "Selenium Test Garage"

        # 1. Log in using the same steps as your working login test.
        driver.get(f"{BASE_URL}/web/login?{database_query}")
        login_box = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "login"))
        )
        login_box.clear()
        login_box.send_keys(USERNAME)
        password_box = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        password_box.clear()
        password_box.send_keys(PASSWORD)
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "form.oe_login_form button[type='submit']")
            )
        ).click()
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".o_user_menu")),
            message="Login did not finish. Check the database and account settings.",
        )

        # 2. Open Fleet's Vehicles screen, then click New.
        # The action name comes from your project's fleet_vehicle_views.xml.
        driver.get(
            f"{BASE_URL}/web?{database_query}#action=fleet.fleet_vehicle_action"
        )
        self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".o-kanban-button-new, .o_list_button_add")
            ),
            message="Vehicles did not open. Check Fleet installation and permissions.",
        ).click()

        # 3. Select an existing model from the dropdown.
        # Model is a relationship field: typing a name alone does not select it.
        model_box = self.vehicle_input("model_id")
        model_box.clear()
        model_box.click()
        model_option = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".o_form_view .o_field_widget[name='model_id'] "
                    "li.o-autocomplete--dropdown-item"
                    ":not(.o_m2o_dropdown_option)"
                    ":not(.o_m2o_start_typing)"
                    ":not(.o_m2o_no_result) a:not(.o_loading)",
                )
            ),
            message="No existing model appeared. Add a Fleet model, then rerun.",
        )
        # The selector excludes Create, Search More, and other helper entries.
        selected_model = model_option.text.strip()
        self.assertTrue(selected_model, "The selected model must have a name.")
        model_option.click()
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (
                    By.CSS_SELECTOR,
                    ".o_form_view .o_field_widget[name='model_id'] input",
                ),
                selected_model,
            )
        )

        # 4. Enter a unique plate and a location. Tab applies each input change.
        plate_box = self.vehicle_input("license_plate")
        plate_box.clear()
        plate_box.send_keys(license_plate, Keys.TAB)
        location_box = self.vehicle_input("location")
        location_box.clear()
        location_box.send_keys(location, Keys.TAB)

        # 5. Save. Odoo 18 may show this button as a cloud-upload icon.
        save_locator = (By.CSS_SELECTOR, ".o_form_button_save")
        self.wait.until(EC.element_to_be_clickable(save_locator)).click()
        self.wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".o_form_status_indicator_new_record")
            ),
            message="The vehicle is still unsaved. Check for a validation error.",
        )
        self.wait.until(EC.invisibility_of_element_located(save_locator))

        # 6. Reload the page to read the saved record back from Odoo.
        driver.refresh()
        saved_model = self.vehicle_input("model_id").get_property("value")
        saved_plate = self.vehicle_input("license_plate").get_property("value")
        saved_location = self.vehicle_input("location").get_property("value")

        # 7. Assertions compare the saved values with what we entered.
        self.assertEqual(saved_model, selected_model, "The vehicle model was not saved.")
        self.assertEqual(saved_plate, license_plate, "The license plate was not saved.")
        self.assertEqual(saved_location, location, "The vehicle location was not saved.")
        print(f"\nVerified saved vehicle: {selected_model} / {license_plate}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
