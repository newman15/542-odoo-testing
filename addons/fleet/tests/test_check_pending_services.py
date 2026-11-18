from odoo.tests.common import TransactionCase

class TestCheckPendingServices(TransactionCase):

    # Verify that a given vehicle has no pending services
    def test_01_vehicle_blocked(self):
        brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Hyundai"
        })

        model = self.env["fleet.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "Kona EV"
        })

        test_vehicle = self.env["fleet.vehicle"].create({
            "model_id": model.id,
        })
        service_log = self.env["fleet.vehicle.log.services"].create({
            "vehicle_id": test_vehicle.id,
            "description": "Arbitrary Service",
            "state": "new"
        })

        vehicle_ready_pre = self.check_for_pending_services(test_vehicle)
        self.assertFalse("Vehicle with pending services is not ready for operation")

        service_log.write({"state": "done"})
        vehicle_ready_post = self.check_for_pending_services(test_vehicle)
        self.assertTrue("Vehicle with no pending services is ready for operation")

    def test_02_vehicle_ready(self):
        brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Hyundai"
        })

        model = self.env["fleet.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "Elantra"
        })

        test_vehicle = self.env["fleet.vehicle"].create({
            "model_id": model.id,
        })
        vehicle_ready = self.check_for_pending_services(test_vehicle)
        self.assertTrue("Vehicle is ready for operation")

    def check_for_pending_services(self, test_vehicle):
        pending_service_count = self.env["fleet.vehicle.log.services"].search_count([
            ("vehicle_id", '=', test_vehicle.id),
            ("state", "in", ["new", "running"])
        ])
        return (pending_service_count == 0)