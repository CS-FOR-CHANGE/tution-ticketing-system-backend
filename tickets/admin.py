from django.contrib import admin
from .models import (
    Organization, Subject, Ticket, TicketingCode
)

admin.site.register(Organization)
admin.site.register(Subject)
admin.site.register(Ticket)
admin.site.register(TicketingCode)