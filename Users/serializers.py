from rest_framework import serializers
from .models import Student, Tutor
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import IntegrityError
import uuid
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class StudentSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'name', 'pronouns', 'photo', 'user_email']
        
    def get_user_email(self, obj):
        # Return the email of the related user
        return obj.user.email


class TutorSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    tickets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Tutor
        fields = ['id', 'name', 'pronouns', 'photo', 'tickets', 'user_email']
        
    def get_user_email(self, obj):
        # Return the email of the related user
        return obj.user.email


class UserRegistrationSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)  # For user input
    pronouns = serializers.CharField(
        write_only=True, allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'pronouns']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with that email already exists.")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        email = validated_data.get('email')
        pronouns = validated_data.get('pronouns', '')
        password = validated_data.get('password')

        # Split the full name into first name and last name (simplified)
        name_parts = full_name.split(' ')
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Generate a unique username
        username = self.generate_unique_username(email)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        except IntegrityError:
            # Handle the unlikely case where the generated username is not unique
            user = self.handle_username_collision(
                username, email, password, first_name, last_name)

        # Now, create a Student instance for this user
        student = Student.objects.create(
            user=user,
            name=full_name,  # Using the full name as the student's name
            pronouns=pronouns
        )

        return user

    def generate_unique_username(self, email):
        base_username = email.split('@')[0]
        unique_username = base_username
        counter = 1
        while User.objects.filter(username=unique_username).exists():
            unique_username = f'{base_username}_{counter}'
            counter += 1
        return unique_username

    def handle_username_collision(self, base_username, email, password, first_name, last_name):
        # Generate a new username with a UUID to ensure uniqueness
        unique_username = f'{base_username}_{uuid.uuid4().hex[:8]}'
        return User.objects.create_user(
            username=unique_username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        # Use email as the primary identifier for authentication
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate the user using email
        user = authenticate(request=self.context.get(
            'request'), username=email, password=password)

        if user is not None:
            # Add custom claims or additional user data here, if needed
            data = super().validate(attrs)
            # data.update({'custom_field': 'custom_data'})  # Example of adding custom data to the token payload
            return data
        else:
            raise AuthenticationFailed(
                'No active account found with the given credentials')
