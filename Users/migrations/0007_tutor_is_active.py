# Generated by Django 5.0.2 on 2024-04-04 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0006_student_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]