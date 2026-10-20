from odoo.tests.common import TransactionCase


class TestHospitalSmoke(TransactionCase):

    def test_hospital_patient_model_available(self):
        """Verify that the Hospital patient model is available."""
        self.assertIn('hospital.patient', self.env)