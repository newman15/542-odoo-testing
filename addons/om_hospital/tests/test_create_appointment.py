from uuid import uuid4

from psycopg2.errors import ForeignKeyViolation

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHospitalAppointmentMissingDoctor(TransactionCase):
    # Odoo supplies self.env and rolls back this test's record changes afterward.

    def test_create_appointment_without_doctor_two(self):
        """Expose the wizard's hard-coded doctor as a failing regression test."""
        # self.env gives access to Odoo models through its ORM (database API).
        # Include archived doctors: archiving hides a row but does not delete it.
        doctors = self.env['hospital.doctor'].with_context(active_test=False)
        # browse() refers to an ID; exists() checks whether that row is present.
        doctor_two = doctors.browse(2).exists()
        if doctor_two:
            # Keep existing appointments valid, including those already done.
            # TransactionCase rolls back both reassignment and deletion.
            replacement = doctors.create({'doctor_name': 'Appointment test doctor'})
            self.assertNotEqual(replacement.id, 2)
            self.env['hospital.appointment'].search([
                ('doctor_id', '=', 2),
            ]).write({'doctor_id': replacement.id})
            doctor_two.unlink()

        self.assertFalse(doctors.browse(2).exists())
        # Patient names must be unique and age cannot be zero. Supply valid data
        # so an unrelated validation error does not hide the doctor bug.
        patient = self.env['hospital.patient'].create({
            'name': f'Appointment test patient {uuid4().hex}',
            'age': 30,
            'gender': 'female',
        })
        appointment_date = fields.Date.today()
        # A wizard is the temporary record behind an Odoo dialog. Calling its
        # button method exercises the same creation logic as clicking Create.
        wizard = self.env['create.appointment.wizard'].create({
            'patient_id': patient.id,
            'date_appointment': appointment_date,
        })

        try:
            # A SQL error leaves PostgreSQL's transaction unusable until rollback.
            # This inner savepoint rolls back the attempted appointment before
            # we report the failure; the outer test rollback restores the doctor.
            with self.env.cr.savepoint():
                action = wizard.action_create_appointment()
                # Send pending ORM changes to PostgreSQL so DB errors occur here.
                self.env.flush_all()
        except ForeignKeyViolation as error:
            # Only translate the known doctor error. Let unrelated errors surface.
            if error.diag.constraint_name != 'hospital_appointment_doctor_id_fkey':
                raise
            # This is deliberately a failing bug demonstration, not assertRaises:
            # catching the expected exception as a success would mark it PASS.
            self.fail(
                'Appointment creation failed because the wizard hard-codes '
                'doctor_id=2, but that doctor does not exist.'
            )

        # If creation succeeds, the returned UI action should open the new record.
        self.assertEqual(action['res_model'], 'hospital.appointment')
        appointment = self.env['hospital.appointment'].browse(action['res_id']).exists()
        self.assertTrue(appointment, 'The wizard must create an appointment.')
        self.assertEqual(appointment.patient_id, patient)
        self.assertEqual(appointment.date_appointment, appointment_date)
        self.assertTrue(appointment.doctor_id.exists())
