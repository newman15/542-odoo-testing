"""Positive test: create a valid patient and confirm the patient record."""

from uuid import uuid4

from odoo.tests.common import TransactionCase


class TestHospitalPatientPositive(TransactionCase):

    def test_create_and_confirm_patient(self):
        """A valid new patient can move from Draft to Confirmed."""
        # Arrange: create our own patient with a unique name and valid age.
        patient_name = f"Positive test patient {uuid4().hex}"
        patient = self.env["hospital.patient"].create({
            "name": patient_name,
            "age": 30,
            "gender": "female",
        })

        # Check that the patient was created with the expected information.
        self.assertTrue(patient.exists(), "The patient should be created.")
        self.assertEqual(patient.name, patient_name)
        self.assertEqual(patient.age, 30)
        self.assertEqual(patient.gender, "female")
        self.assertEqual(patient.state, "draft")

        # Act: call the Hospital method that confirms a patient.
        patient.action_confirm()

        # Assert: confirmation should change the patient's status.
        self.assertEqual(
            patient.state,
            "confirm",
            "Confirming the patient should set the status to Confirmed.",
        )
