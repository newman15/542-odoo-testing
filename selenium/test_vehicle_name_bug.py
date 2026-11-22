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

