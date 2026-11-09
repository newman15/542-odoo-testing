

from psycopg2.errors import NotNullViolation

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestFleetVehicleCreation(TransactionCase):
    """Accept valid vehicle data and reject a missing required model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create our own manufacturer and model instead of using demo data.
        cls.brand = cls.env["fleet.vehicle.model.brand"].create({
            "name": "QA Test Manufacturer",
        })
        cls.vehicle_model = cls.env["fleet.vehicle.model"].create({
            "name": "QA Test Model",
            "brand_id": cls.brand.id,
            "vehicle_type": "car",
        })

    def test_create_vehicle_with_model(self):
        """Positive: a vehicle with a valid model is saved correctly."""
        vehicle = self.env["fleet.vehicle"].create({
            "model_id": self.vehicle_model.id,
            "license_plate": "QA-POS-542",
            "odometer_unit": "kilometers",
        })

        self.assertTrue(vehicle.exists(), "The vehicle should be created.")
        self.assertEqual(vehicle.model_id, self.vehicle_model)
        self.assertEqual(vehicle.license_plate, "QA-POS-542")
        self.assertEqual(vehicle.odometer_unit, "kilometers")

    def test_reject_vehicle_without_model(self):
        """Negative: a missing model is rejected and no vehicle is added."""
        Vehicle = self.env["fleet.vehicle"]
        domain = [("license_plate", "=", "QA-NEG-542")]
        count_before = Vehicle.search_count(domain)

        # Suppress only the expected SQL error log for this invalid operation.
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(ValidationError) as caught:
                # The savepoint rolls back the failed database operation
                # before assertRaises catches the expected exception.
                with self.env.cr.savepoint():
                    Vehicle.create({
                        "model_id": self.vehicle_model.id,
                        "license_plate": "QA-NEG-542",
                        "odometer_unit": "kilometers",
                    })

        # Check that rejection was specifically for the missing vehicle model.
        self.assertEqual(caught.exception.diag.table_name, "fleet_vehicle_model"
        self.assertEqual(caught.exception.diag.column_name, "license_plate")
        self.assertEqual(Vehicle.search_count(domain), count_before)
