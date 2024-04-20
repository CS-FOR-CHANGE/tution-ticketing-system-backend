# Generated by Django 5.0.2 on 2024-04-04 18:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0007_tutor_is_active'),
        ('tickets', '0006_subject_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_tutors', to='tickets.organization')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_organizations', to='Users.tutor')),
            ],
            options={
                'verbose_name_plural': 'Tutor Organizations',
                'unique_together': {('tutor', 'organization')},
            },
        ),
    ]