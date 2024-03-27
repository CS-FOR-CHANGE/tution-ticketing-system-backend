from django.contrib import admin
from .models import (
    Student, Tutor
)
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class TutorAdminForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, help_text="The tutor's unique email address.")
    password = forms.CharField(
        widget=forms.PasswordInput, required=True, help_text="The tutor's password.")

    class Meta:
        model = Tutor
        fields = '__all__'
        exclude = ('user',)  # Exclude the user field from the form

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        tutor = super().save(commit=False)  # Call the superclass
        if not self.instance.pk:  # Check if this is a new instance
            user, created = User.objects.get_or_create(
                email=self.cleaned_data['email'],
                defaults={'username': self.cleaned_data['email']}
            )
            if created:
                user.set_password(self.cleaned_data['password'])
                user.save()
            tutor.user = user
        if commit:
            tutor.save()
        return tutor


class TutorAdmin(admin.ModelAdmin):
    form = TutorAdminForm
    # Optionally, you can specify which fields to show in the form explicitly
    # fields = ('name', 'pronouns', 'photo', 'tickets', 'email', 'password')


admin.site.register(Tutor, TutorAdmin)
admin.site.register(Student)
