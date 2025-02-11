from django.urls import reverse

from service_catalog.models import GlobalHook
from tests.test_service_catalog.base import BaseTest


class GlobalHookDeleteViewsTest(BaseTest):

    def setUp(self):
        super(GlobalHookDeleteViewsTest, self).setUp()
        self.global_hook_test = GlobalHook.objects.create(name="hook1",
                                                          model="Instance",
                                                          state="PROVISIONING",
                                                          job_template=self.job_template_test)
        args = {
            "global_hook_id": self.global_hook_test.id
        }
        self.url = reverse('service_catalog:global_hook_delete', kwargs=args)

    def test_can_delete_global_hook(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        id_to_delete = self.global_hook_test.id
        response = self.client.post(self.url)
        self.assertEqual(302, response.status_code)
        self.assertFalse(GlobalHook.objects.filter(id=id_to_delete).exists())

    def test_cannot_delete_global_hook_when_logout(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(302, response.status_code)
