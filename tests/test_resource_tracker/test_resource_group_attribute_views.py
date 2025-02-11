from copy import copy

from django.urls import reverse

from resource_tracker.models import ResourceGroupAttributeDefinition, ResourcePool, ResourceGroup
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestResourceGroupAttributeViews(BaseTestResourceTracker):

    def setUp(self):
        super(TestResourceGroupAttributeViews, self).setUp()

    def test_resource_group_attribute_create(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
        }
        url = reverse('resource_tracker:resource_group_attribute_create', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue("resource_group" in response.context)

        # test POST without producer or consumer
        new_name = "new_attribute_name"
        data = {
            "name": new_name
        }
        number_attribute_before = ResourceGroupAttributeDefinition.objects.all().count()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(number_attribute_before + 1, ResourceGroupAttributeDefinition.objects.all().count())
        self.assertTrue(ResourceGroupAttributeDefinition.objects.filter(name="new_attribute_name",
                                                                        resource_group=self.rg_physical_servers).exists())

        # test POST with producer
        new_name = "new_attribute_name_2"
        data = {
            "name": new_name,
            "produce_for": self.rp_vcenter_vcpu_attribute.id
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(ResourceGroupAttributeDefinition.objects.filter(name="new_attribute_name_2",
                                                                        resource_group=self.rg_physical_servers).exists())
        target_rga = ResourceGroupAttributeDefinition.objects.get(name="new_attribute_name_2",
                                                                  resource_group=self.rg_physical_servers)
        self.assertEqual(target_rga.produce_for, self.rp_vcenter_vcpu_attribute)

        # test POST with already exist attribute
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(f"Attribute {new_name} already exist in {self.rg_physical_servers.name}",
                         response.context['form'].errors['name'][0])

    def test_cannot_create_resource_group_attribute_when_logout(self):
        self.client.logout()
        args = {
            "resource_group_id": self.rg_physical_servers.id,
        }
        url = reverse('resource_tracker:resource_group_attribute_create', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_attribute_edit(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_cpu_attribute.id
        }
        url = reverse('resource_tracker:resource_group_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST without producer or consumer
        new_name = "new_attribute_name"
        data = {
            "name": new_name
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_cpu_attribute.name, "new_attribute_name")

    def test_cannot_edit_resource_group_attribute_when_logout(self):
        self.client.logout()
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_cpu_attribute.id
        }
        url = reverse('resource_tracker:resource_group_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_attribute_edit_existing_name(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_cpu_attribute.id
        }
        url = reverse('resource_tracker:resource_group_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST without producer or consumer
        new_name = self.rg_physical_servers_memory_attribute.name
        data = {
            "name": new_name
        }
        old_name = self.rg_physical_servers_cpu_attribute.name
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_cpu_attribute.name, old_name)

    def test_resource_group_attribute_edit_same_name(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_cpu_attribute.id
        }
        url = reverse('resource_tracker:resource_group_attribute_edit', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST without producer or consumer
        data = {
            "name": self.rg_physical_servers_cpu_attribute.name,
            "produce_for": "",
            "consume_from": ""
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.rg_physical_servers_cpu_attribute.refresh_from_db()
        self.assertEqual(self.rg_physical_servers_cpu_attribute.produce_for, None)
        self.assertEqual(self.rg_physical_servers_cpu_attribute.consume_from, None)

    def test_resource_group_attribute_delete(self):
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_cpu_attribute.id
        }
        url = reverse('resource_tracker:resource_group_attribute_delete', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # test POST
        attribute_id = copy(self.rg_physical_servers_cpu_attribute.id)
        self.assertTrue(ResourceGroupAttributeDefinition.objects.filter(id=attribute_id).exists())
        response = self.client.post(url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(ResourceGroupAttributeDefinition.objects.filter(id=attribute_id).exists())

    def test_cannot_delete_resource_group_attribute_logout(self):
        self.client.logout()
        args = {
            "resource_group_id": self.rg_physical_servers.id,
            "attribute_id": self.rg_physical_servers_cpu_attribute.id
        }
        url = reverse('resource_tracker:resource_group_attribute_delete', kwargs=args)

        # test GET
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_resource_group_attribute_add_producer_pool_is_updated(self):
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_pool_vcpu_att = vcenter_pool.add_attribute_definition(name='vCPU')
        server_group = ResourceGroup.objects.create(name="server-group")
        server_cpu_attribute_def = server_group.add_attribute_definition(name='CPU')
        server = server_group.create_resource(name=f"server-group1")
        server.set_attribute(server_cpu_attribute_def, 100)
        # nothing produced yet
        self.assertEqual(0, vcenter_pool_vcpu_att.total_produced)

        args = {
            "resource_group_id": server_group.id,
            "attribute_id": server_cpu_attribute_def.id
        }
        url = reverse('resource_tracker:resource_group_attribute_edit', kwargs=args)

        data = {
            "name": server_group.name,
            "produce_for": vcenter_pool_vcpu_att.id,
            "consume_from": ""
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        vcenter_pool_vcpu_att.refresh_from_db()
        self.assertEqual(100, vcenter_pool_vcpu_att.total_produced)

    def test_resource_group_attribute_delete_producer_pool_is_updated(self):
        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_pool_vcpu_att = vcenter_pool.add_attribute_definition(name='vCPU')
        server_group = ResourceGroup.objects.create(name="server-group")
        server_cpu_attribute_def = server_group.add_attribute_definition(name='CPU')
        server = server_group.create_resource(name=f"server-group1")
        server.set_attribute(server_cpu_attribute_def, 100)
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group.attribute_definitions.get(name='CPU'))
        vcenter_pool_vcpu_att.refresh_from_db()
        self.assertEqual(100, vcenter_pool_vcpu_att.total_produced)

        args = {
            "resource_group_id": server_group.id,
            "attribute_id": server_cpu_attribute_def.id
        }
        url = reverse('resource_tracker:resource_group_attribute_edit', kwargs=args)

        data = {
            "name": server_group.name,
            "produce_for": "",
            "consume_from": ""
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        vcenter_pool_vcpu_att.refresh_from_db()
        self.assertEqual(0, vcenter_pool_vcpu_att.total_produced)
