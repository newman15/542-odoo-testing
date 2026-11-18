"""Check that a user can log in to our local Odoo website.

Before running this file:
    1. Start Odoo with Docker and create your database and user.
    2. Install Google Chrome on your computer.
    3. Activate the virtual environment where you installed Selenium.
    4. Check the settings below against the database and user you created.

From the project folder, run:
    python selenium/test_login.py

The browser opens so we can watch the test. Python prints OK if it passes,
or shows the failed check or error if something goes wrong. This test uses
the running Odoo website; it does not start Docker or create a database.
"""

import unittest
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Change these if you chose a different database, email, or password.
BASE_URL = "http://localhost:8069"
DATABASE = "odoo18"
USERNAME = "admin@example.com"
PASSWORD = "admin"
WAIT_SECONDS = 20


class TestOdooLogin(unittest.TestCase):
    """Group the steps and checks for logging in successfully."""

    def setUp(self):
        # Initialize the chrom driver
        self.driver = webdriver.Chrome()

        # Limit how long opening a page can take if Odoo is not responding.
        self.driver.set_page_load_timeout(30)

        # Odoo loads parts of its screen after the page opens. This lets us
        # wait for the part we need instead of guessing with time.sleep().
        self.wait = WebDriverWait(self.driver, WAIT_SECONDS)

    def test_successful_login(self):
        """Valid account details should open Odoo's signed-in screen."""
        driver = self.driver

        # The db part tells Odoo which database to use. This avoids choosing
        # one by hand if our Docker setup contains more than one database.
        login_url = f"{BASE_URL}/web/login?{urlencode({'db': DATABASE})}"
        driver.get(login_url)

        # Wait until the login and password boxes are visible on the page
        login_box = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "login"))
        )
        password_box = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )

        # Clear any filled-in text, then type the account details.
        login_box.clear()
        login_box.send_keys(USERNAME)
        password_box.clear()
        password_box.send_keys(PASSWORD)

        # A CSS selector describes the element we want. Here we choose the
        # submit button inside Odoo's login form and click it.
        login_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "form.oe_login_form button[type='submit']")
            )
        )
        login_button.click()

        # A different URL alone would not prove that login worked. Wait for
        # the user menu that Odoo shows in its signed-in application screen.
        # If login fails, this wait times out and unittest reports an error.
        user_menu = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".o_user_menu")),
            message="Odoo's user menu did not appear. Check the login details and database.",
        )
        self.assertTrue(user_menu.is_displayed(), "The user menu should be visible.")

        # Also check that we have left the login form behind.
        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "form.oe_login_form")),
            message="The login form is still visible after signing in.",
        )

    def tearDown(self):
        # closes the whole browser and stops its driver process.
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
