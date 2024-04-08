from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.


class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class OrganizationTutor(models.Model):
    tutor = models.ForeignKey("Users.Tutor", on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='organization_tutors')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate the tutor in other organizations
            OrganizationTutor.objects.filter(
                tutor=self.tutor, 
                is_active=True
            ).exclude(
                id=self.id
            ).update(is_active=False)

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('tutor', 'organization')

    def __str__(self):
        return f"{self.tutor.name} at {self.organization.name} - {'Active' if self.is_active else 'Inactive'}"


# Now, we add the tutors field to the Organization model using the through model.
Organization.add_to_class('tutors', models.ManyToManyField(
    "Users.Tutor", through=OrganizationTutor, related_name='organizations'))


class Subject(models.Model):
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(
        Organization, related_name='organization_subject', on_delete=models.CASCADE, default=1)
    tutors = models.ManyToManyField(
        "Users.Tutor", related_name='tutors_subject')

    def __str__(self):
        return f"{self.title}-{self.organization.name}"


class Ticket(models.Model):
    student = models.ForeignKey(
        "Users.Student", on_delete=models.CASCADE, related_name='student_ticket', default=1)
    tutor = models.ForeignKey(
        "Users.Tutor", on_delete=models.CASCADE, related_name='tutor_ticket', default=1)
    subject = models.ForeignKey(
        'Subject', on_delete=models.CASCADE, related_name='subject_ticket', default=1)
    start_time = models.DateTimeField(
        default=timezone.now, help_text="The start time of the session")
    end_time = models.DateTimeField(help_text="The end time of the session")

    def save(self, *args, **kwargs):
        """Override the save method to set the end time 10 minutes after the start time."""
        if not self.id:  # Check if this is a new instance
            self.end_time = self.start_time + timezone.timedelta(minutes=10)
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject.title} session for {self.student.name} with {self.tutor.name}"


class TicketingCode(models.Model):
    code = models.IntegerField()

    class Meta:
        verbose_name = "Ticketing Code"
        verbose_name_plural = "Ticketing Code"

    def save(self, *args, **kwargs):
        if TicketingCode.objects.exists() and not self.pk:
            # If you're trying to save a new instance and an instance already exists, raise an exception
            raise ValidationError(
                'There can be only one TicketingCode instance')
        return super().save(*args, **kwargs)
