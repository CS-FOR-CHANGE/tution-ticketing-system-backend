from django.contrib import admin
from .models import (
    Organization, Subject, TicketingCode, OrganizationTutor
)


class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description',
                     'organization__name', 'tutors__name']
    list_display = ('title', 'is_active', 'organization_name', 'list_tutors')
    # Allows in-place editing of is_active in the list view
    list_editable = ('is_active',)
    list_filter = ('is_active',)  # Adds a filter for is_active on the sidebar

    def organization_name(self, obj):
        return obj.organization.name
    organization_name.short_description = 'Organization'

    def list_tutors(self, obj):
        return ", ".join([tutor.name for tutor in obj.tutors.all()])
    list_tutors.short_description = 'Tutors'

class OrganizationTutorInline(admin.TabularInline):
    model = OrganizationTutor
    extra = 1  # Adjust as needed

class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationTutorInline]
    list_display = ('name', 'description', 'list_active_tutors')
    
    def list_active_tutors(self, obj):
        active_tutors = obj.organization_tutors.filter(is_active=True)
        return ", ".join(tutor.tutor.name for tutor in active_tutors)
    list_active_tutors.short_description = 'Active Tutors'


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(TicketingCode)
