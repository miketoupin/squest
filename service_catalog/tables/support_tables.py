from django_tables2 import tables, TemplateColumn, LinkColumn
from django_tables2.utils import A

from service_catalog.models import Support
from Squest.utils.squest_table import SquestTable


class SupportTable(SquestTable):
    state = TemplateColumn(template_name='custom_columns/support_state.html')
    date_opened = TemplateColumn(template_name='custom_columns/generic_date_format.html')
    title = LinkColumn("service_catalog:instance_support_details", args=[A("instance__id"), A("id")])
    instance__name = LinkColumn("service_catalog:instance_details", args=[A("instance__id")],
                                verbose_name="Instance")

    class Meta:
        model = Support
        attrs = {"id": "support_table", "class": "table squest-pagination-tables"}
        fields = ("title", "instance__name", "opened_by", "date_opened", "state")
