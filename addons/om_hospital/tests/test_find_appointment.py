from uuid import uuid4

from odoo import fields
from odoo.tests.common import TransactionCase
from psycopg2.errors import ForeignKeyViolation

class TestFindAppointment(TransactionCase):
    # Odoo supplies self.env and rolls back this test's record changes afterward.
    """Find appointment with invalid patient id"""
    def test_find_appointment_without_patient(self): 

        self.test_m1()
        self.test_m2()
        self.test_m3()

    def test_m1(self):
        false_id = -111
        try:
            wizard_m1 = self.env['search.appointment.wizard'].create({
                        'patient_id': false_id
                    })
            wizard_m1.action_search_appointment_m1()
        except ForeignKeyViolation as error_m1:
            if error_m1.diag.constraint_name != 'search_appointment_wizard_patient_id_fkey':
                raise
            self.fail(
                f'Appointment search via M1 failed because no patient with id {false_id} exists.'
            )

    def test_m2(self):
        false_id = -222
        try:
            wizard_m2 = self.env['search.appointment.wizard'].create({
                        'patient_id': false_id
                    })
            wizard_m2.action_search_appointment_m2()
        except ForeignKeyViolation as error_m2:
            if error_m2.diag.constraint_name != 'search_appointment_wizard_patient_id_fkey':
                raise
            self.fail(
                f'Appointment search via M2 failed because no patient with id {false_id} exists.'
            )

    def test_m3(self):
        false_id = -333
        try:
            wizard_m3 = self.env['search.appointment.wizard'].create({
                        'patient_id': false_id
                    })
            wizard_m3.action_search_appointment_m2()
        except ForeignKeyViolation as error_m3:
            if error_m3.diag.constraint_name != 'search_appointment_wizard_patient_id_fkey':
                raise
            self.fail(
                f'Appointment search via M3 failed because no patient with id {false_id} exists.'
            )
