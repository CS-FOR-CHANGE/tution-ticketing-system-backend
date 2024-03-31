from django.contrib import admin
from .models import (
    Organization, Subject, Ticket, TicketingCode
)


class SubjectAdmin(admin.ModelAdmin):
    # Enables searching by title and description directly on the Subject model,
    # and also through related fields like the organization's name and tutor's name.
    search_fields = ['title', 'description', 'organization__name', 'tutors__name']
    
    # Customizes what columns to display in the list view. Adjust as needed.
    list_display = ('title', 'organization_name', 'list_tutors')

    # Method to display the organization's name in the list_display
    def organization_name(self, obj):
        return obj.organization.name
    organization_name.short_description = 'Organization'

    # Method to display a comma-separated list of tutors for each subject
    def list_tutors(self, obj):
        return ", ".join([tutor.name for tutor in obj.tutors.all()])
    list_tutors.short_description = 'Tutors'

admin.site.register(Organization)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Ticket)
admin.site.register(TicketingCode)