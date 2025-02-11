from rest_framework import status
from rest_framework.reverse import reverse

from service_catalog.models import InstanceState, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestInstanceCreate(BaseTestRequest):

    def setUp(self):
        super(TestInstanceCreate, self).setUp()
        self.url = reverse('api_instance_list')

    def _assert_created(self, data, expected):
        instance_count = Instance.objects.count()
        response = self.client.post(self.url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(instance_count + 1, Instance.objects.count())
        self.assertEqual(response.data['name'], expected['name'])
        self.assertEqual(response.data['service'], expected['service'])
        self.assertEqual(response.data['spoc']['id'], expected['spoc'])
        if response.data['billing_group']:
            self.assertEqual(response.data['billing_group']['id'], expected['billing_group'])
        self.assertEqual(response.data['spec'], expected['spec'])
        self.assertEqual(response.data['resources'], expected['resources'])

    def test_instance_create_all_field(self):
        data = {
            "name": "instance_create_test_1",
            "service": self.service_test_2.id,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.AVAILABLE,
            "billing_group": self.test_billing_group.id,
            "spec": {
                "key1": "val1",
                "key2": "val2"
            }
        }
        expected = {'state': 'AVAILABLE',
                    'name': 'instance_create_test_1',
                    'spec': {'key1': 'val1', 'key2': 'val2'},
                    'service': self.service_test_2.id,
                    'spoc': self.standard_user_2.id,
                    'resources': [],
                    'billing_group': self.test_billing_group.id}
        self._assert_created(data, expected)

    def test_instance_create_spec_empty_dict(self):
        data = {
            "name": "instance_create_test_2",
            "service": self.service_test_2.id,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.UPDATING,
            "billing_group": None,
            "spec": {}
        }
        expected = {'state': 'UPDATING',
                    'name': 'instance_create_test_2',
                    'spec': {},
                    'service': self.service_test_2.id,
                    'spoc': self.standard_user_2.id,
                    'resources': [],
                    'billing_group': None}
        self._assert_created(data, expected)

    def test_instance_create_no_service(self):
        data = {
            "name": "instance_create_test_3",
            "service": None,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.PROVISIONING,
            "billing_group": None,
            "spec": {
            }
        }
        expected = {'state': 'PROVISIONING',
                    'name': 'instance_create_test_3',
                    'spec': {},
                    'service': None,
                    'spoc': self.standard_user_2.id,
                    'resources': [],
                    'billing_group': None}
        self._assert_created(data, expected)

    def test_non_admin_cannot_create_instance(self):
        self.client.force_login(user=self.standard_user)
        data = {
            "name": "instance_create_test_1",
            "service": self.service_test_2.id,
            "spoc": self.standard_user_2.id,
            "state": InstanceState.AVAILABLE,
            "billing_group": self.test_billing_group.id,
            "spec": {
                "key1": "val1",
                "key2": "val2"
            }
        }
        response = self.client.post(self.url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
