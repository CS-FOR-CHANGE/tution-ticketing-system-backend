from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Establishes the one-to-one relation
    name = models.CharField(max_length=100)
    pronouns = models.CharField(max_length=50)  # Example: "he/him", "they/them", etc.
    photo = models.ImageField(upload_to='tutor_photos/', blank=True, null=True)
    tickets = models.ManyToManyField('tickets.Ticket', related_name='tickets_tutor', blank=True)

    def __str__(self):
        return f"{self.name} ({self.pronouns})-{self.id}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Establishes the one-to-one relation
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='tutor_photos/', blank=True, null=True)
    pronouns = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        pronouns_display = f" ({self.pronouns})" if self.pronouns else ""
        return f"{self.name}{pronouns_display}-{self.id}"