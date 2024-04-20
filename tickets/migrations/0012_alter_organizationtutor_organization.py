# Generated by Django 5.0.2 on 2024-04-04 18:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0011_organizationtutor_organization_tutors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationtutor',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_tutors', to='tickets.organization'),
        ),
    ]