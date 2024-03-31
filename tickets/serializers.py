from rest_framework import serializers
from .models import Subject, Ticket, Organization
from Users.serializers import TutorSerializer, StudentSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description']


class SubjectSerializer(serializers.ModelSerializer):
    tutors = TutorSerializer(many=True, read_only=True)
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'title', 'description', 'organization', 'tutors']


class TicketSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    tutor = TutorSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'student', 'tutor', 'subject', 'session_time']
