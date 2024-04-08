from rest_framework import serializers
from .models import Subject, Ticket, Organization, OrganizationTutor
from Users.serializers import TutorSerializer, StudentSerializer


class OrganizationTutorSerializer(serializers.ModelSerializer):
    tutor = TutorSerializer(read_only=True)

    class Meta:
        model = OrganizationTutor
        fields = ['tutor', 'is_active']


class OrganizationSerializer(serializers.ModelSerializer):
    active_tutors = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'active_tutors']

    def get_active_tutors(self, obj):
        # Filter OrganizationTutor instances for this organization where is_active=True
        active_tutor_relations = obj.organization_tutors.filter(is_active=True)
        # Extract tutor instances from these relationships
        active_tutors = [relation.tutor for relation in active_tutor_relations]
        # Serialize the tutor instances
        return TutorSerializer(active_tutors, many=True).data


class SubjectSerializer(serializers.ModelSerializer):
    tutors = serializers.SerializerMethodField()
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ['is_active', 'id', 'title',
                  'description', 'organization', 'tutors']

    def get_tutors(self, obj):
        # First, filter tutors based on the direct ManyToMany relationship to the subject
        subject_tutors = obj.tutors.all()

        # Next, filter these tutors further to only include those who are active in the subject's organization
        active_organization_tutors = OrganizationTutor.objects.filter(
            tutor__in=subject_tutors, 
            organization=obj.organization, 
            is_active=True
        ).select_related('tutor')

        # Extracting Tutor instances from these active organization-tutor relationships
        active_tutors = [org_tutor.tutor for org_tutor in active_organization_tutors]

        # Now serialize the filtered queryset of Tutors
        return TutorSerializer(active_tutors, many=True, context={'request': self.context.get('request')}).data


class TicketSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    tutor = TutorSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'student', 'tutor',
                  'subject', 'start_time', 'end_time']
