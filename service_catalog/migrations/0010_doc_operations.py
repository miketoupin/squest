# Generated by Django 3.2.13 on 2022-09-12 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0009_auto_20220804_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='doc',
            name='operations',
            field=models.ManyToManyField(blank=True, help_text='Operations linked to this doc.', related_name='docs', related_query_name='doc', to='service_catalog.Operation'),
        ),
    ]
