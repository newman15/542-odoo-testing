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

class TestCreateAppointment(unittest.TestCase):
    def setUp(self):
            # Initialize the chrom driver
            self.driver = webdriver.Chrome()

            # Limit how long opening a page can take if Odoo is not responding.
            self.driver.set_page_load_timeout(30)

            # Odoo loads parts of its screen after the page opens. This lets us
            # wait for the part we need instead of guessing with time.sleep().
            self.wait = WebDriverWait(self.driver, WAIT_SECONDS)

    def test_fail_create_appointment(self):
        self.login_to_odoo()

        # Navigate to create appointment
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".o_navbar_apps_menu button"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Hospital')]"))).click()

        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Appointments')] | //a[contains(., 'Appointments')]"))
        ).click()
        submenus = self.driver.find_elements(
            By.XPATH, "//a[contains(@class, 'dropdown-item') and contains(., 'Appointment')]"
        )
        if submenus:
            submenus[1].click()

        # Ensure form view is ready
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".o_form_view")))


        create_button = self.driver.find_element(By.CSS_SELECTOR, "button[name='action_create_appointment']")
        create_button.click()

        invalid_field = self.wait.until(
             EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='alert']")),
             message="No inputs. Alert thrown. Failed"
        )
        self.assertIsNotNone(invalid_field)

    def login_to_odoo(self):
        self.driver.get(f"{BASE_URL}/web/login?{urlencode({'db': DATABASE})}")
        login_field = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "login"))
        )
        password_field = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )

        login_field.clear()
        login_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)

        login_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "form.oe_login_form button[type='submit']")
            )
        )
        login_button.click()
     

    def tearDown(self):
        # closes the whole browser and stops its driver process.
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
