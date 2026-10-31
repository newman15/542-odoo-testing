from odoo.tests.common import TransactionCase


class TestFleetOdometer(TransactionCase):
    # TransactionCase supplies an Odoo environment and rolls back our test data.

    def test_increase_odometer_preserves_history(self):
        """Increasing a vehicle's reading retains both odometer entries."""
        # Build our own records so the test works without demo or manually entered
        # data. self.env['model.name'] accesses a model through Odoo's ORM.
        brand = self.env['fleet.vehicle.model.brand'].create({
            'name': 'Odometer test brand',
        })
        model = self.env['fleet.vehicle.model'].create({
            'name': 'Odometer test model',
            # Relationship fields take the related record's database ID.
            'brand_id': brand.id,
        })
        vehicle = self.env['fleet.vehicle'].create({
            'model_id': model.id,
            'license_plate': 'ODO-TEST',
            'odometer_unit': 'kilometers',
        })

        # write() updates a saved record. Fleet's odometer field has an inverse
        # method: each write adds a history row instead of replacing an old one.
        vehicle.write({'odometer': 1000.0})
        self.assertEqual(vehicle.odometer, 1000.0)
        vehicle.write({'odometer': 1250.0})

        # Clear the cached value so the next read runs Fleet's computation,
        # which takes the highest reading from this vehicle's history.
        vehicle.invalidate_recordset(['odometer'])
        self.assertEqual(vehicle.odometer, 1250.0)
        # The domain (list of filters) limits the search to our vehicle. Sort by
        # value so the assertion does not depend on row IDs or creation order.
        readings = self.env['fleet.vehicle.odometer'].search([
            ('vehicle_id', '=', vehicle.id),
        ], order='value asc')
        self.assertEqual(len(readings), 2)
        # mapped() collects field values from an Odoo recordset. For relationship
        # fields it returns the related records, with duplicates removed.
        self.assertEqual(readings.mapped('value'), [1000.0, 1250.0])
        self.assertEqual(readings.mapped('vehicle_id'), vehicle)
        self.assertEqual(readings.mapped('unit'), ['kilometers', 'kilometers'])
