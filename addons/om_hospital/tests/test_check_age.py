from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHospitalPatient(TransactionCase):

    def test_patient_age_cannot_be_negative(self):
        """Test that negative patient ages are rejected."""

        with self.assertRaises(ValidationError):
            self.env['hospital.patient'].create({
                'name': 'Negative Age Patient',
                'age': -5,
                'gender': 'female',
            })