# Generated by Django 5.0.2 on 2024-04-14 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0012_alter_organizationtutor_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('ready', 'Ready for Help'), ('helping', 'Helping')], default='waiting', help_text='Current status of the ticket', max_length=10),
        ),
    ]
