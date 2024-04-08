from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Subject, Ticket, Organization, TicketingCode, OrganizationTutor
from .serializers import SubjectSerializer, TicketSerializer, OrganizationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.shortcuts import get_object_or_404
from django.http import Http404


class SubjectListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Filter subjects to only include those that are active
        subjects = Subject.objects.filter(is_active=True)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrganizationListView(APIView):
    def get(self, request, format=None):
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateTutorStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, organization_id, tutor_id):
        # Attempt to retrieve the OrganizationTutor instance
        organization_tutor = get_object_or_404(
            OrganizationTutor, organization_id=organization_id, tutor_id=tutor_id)

        # Extract the is_active status from the request data
        is_active = request.data.get('is_active', "").lower() == "true"

        # Validate is_active is provided and is a boolean
        if is_active is None or type(is_active) is not bool:
            return Response({'error': 'The "is_active" field must be a boolean.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the is_active status
        organization_tutor.is_active = is_active
        organization_tutor.save()

        # Return the updated status
        return Response({'is_active': is_active})


class TicketListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Get all the tickets
    def get(self, request, format=None):
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketCreateAPIView(APIView):
    # Create a ticket
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from Users.models import Student, Tutor
        serializer = TicketSerializer(data=request.data)

        # Extract `student_id`, `tutor_id`, and `subject_id`, `ticketing_code` from the request
        student_id = request.data.get('student')
        tutor_id = request.data.get('tutor')
        subject_id = request.data.get('subject')

        subject = Subject.objects.get(id=subject_id)
        student = Student.objects.get(id=student_id)
        tutor = Tutor.objects.get(id=tutor_id)

        ticketing_code = TicketingCode.objects.first()
        user_ticketing_code = request.data.get('ticketing_code')

        if serializer.is_valid():
            if ticketing_code.code == int(user_ticketing_code):
                if Ticket.objects.filter(student_id=student_id).exists():
                    return Response({"error": "Ticket exists for the user"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Manually set the student, tutor, and subject before saving
                    ticket = serializer.save(
                        student=student, tutor=tutor, subject=subject)
                    tutor.tickets.add(ticket)

                    # Now broadcast the new ticket to all connected WebSocket clients
                    channel_layer = get_channel_layer()
                    message = {
                        'action': 'added',
                        'message': json.dumps(TicketSerializer(ticket).data)
                    }

                    async_to_sync(channel_layer.group_send)(
                        "ticket_updates",
                        {
                            "type": "broadcast_message",
                            "message": message
                        }
                    )

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "The provided ticketing code does not match."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDeleteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    """
    View to delete a Ticket instance by ID.
    """

    def get_object(self, pk):
        """
        Helper method to get the object, or raise a 404 if not found.
        """
        try:
            return Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        """
        Attempts to delete the Ticket instance corresponding to the given pk (primary key).
        Returns a success message if deleted successfully, or an error message if an error occurs.
        """
        try:
            user = request.user
            ticket = self.get_object(pk)

            # Check if the request.user is the student or the tutor of the ticket
            if request.user != ticket.student.user and request.user != ticket.tutor.user:
                # If the user is neither the student nor the tutor, deny access
                return Response({"error": "You do not have permission to delete this ticket."},
                                status=status.HTTP_403_FORBIDDEN)

            channel_layer = get_channel_layer()
            message = {
                'action': 'deleted',
                'message': json.dumps(TicketSerializer(ticket).data)
            }

            async_to_sync(channel_layer.group_send)(
                "ticket_updates",
                {
                    "type": "broadcast_message",
                    "message": message
                }
            )

            ticket.delete()
            return Response({"message": "Ticket successfully deleted."}, status=status.HTTP_200_OK)
        except Http404:
            # The ticket does not exist
            return Response({"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Generic exception handling for other unforeseen errors
            # Logging the exception can be helpful for debugging
            # Consider using logging instead of print in production environments
            return Response({"error": "An error occurred while attempting to delete the ticket. Please try again later."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
