from django.urls import path
from .views import (
    SubjectListView, TicketCreateAPIView, TicketListView, OrganizationListView
)

urlpatterns = [
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('organizations/', OrganizationListView.as_view(), name='organization-list'),
    path('tickets/create/', TicketCreateAPIView.as_view(), name='create_ticket'),
]
