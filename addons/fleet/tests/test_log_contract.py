from odoo.tests.common import TransactionCase


class TestFleetVehicleLogContract(TransactionCase):

    def test_compute_next_year_date(self):
        """Test that the method returns a date one year after the input."""

        contract_model = self.env['fleet.vehicle.log.contract']

        result = contract_model.compute_next_year_date('2026-01-15')

        self.assertEqual(result, '2027-01-15')