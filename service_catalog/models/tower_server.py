from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, BooleanField, JSONField
from towerlib import Tower
from django.utils.translation import gettext_lazy as _


class TowerServer(Model):
    name = CharField(max_length=100)
    host = CharField(max_length=200, unique=True)
    token = CharField(max_length=200)
    secure = BooleanField(default=True)
    ssl_verify = BooleanField(default=False)
    extra_vars = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.host})"

    def clean(self):
        if self.extra_vars is None:
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def sync(self, job_template_id=None):
        """
        Sync all job templates
        :return:
        """
        from .job_templates import JobTemplate as JobTemplateLocal
        tower = self.get_tower_instance()
        if job_template_id is None:
            id_in_tower = []
            for job_template_from_tower in tower.job_templates:
                id_in_tower.append(job_template_from_tower.id)
                self._update_job_template_from_tower(job_template_from_tower)
            JobTemplateLocal.objects.filter(tower_server=self).exclude(tower_id__in=id_in_tower).delete()
        else:
            job_template = JobTemplateLocal.objects.get(id=job_template_id)
            self._update_job_template_from_tower(tower.get_job_template_by_id(job_template.tower_id))

    @property
    def url(self):
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.host}"

    def get_tower_instance(self):
        return Tower(self.host, None, None, secure=self.secure, ssl_verify=self.ssl_verify, token=self.token)

    def _update_job_template_from_tower(self, job_template_from_tower):
        from .job_templates import JobTemplate as JobTemplateLocal
        job_template, _ = JobTemplateLocal.objects.get_or_create(tower_id=job_template_from_tower.id,
                                                                 tower_server=self,
                                                                 defaults={'name': job_template_from_tower.name})
        # update data
        job_template.name = job_template_from_tower.name
        job_template.tower_job_template_data = job_template_from_tower._data
        job_template.survey = job_template_from_tower.survey_spec
        job_template.is_compliant = job_template.check_is_compliant()
        job_template.save()
        # update all operation that uses this template
        from service_catalog.models import Operation
        Operation.update_survey_after_job_template_update(job_template)
