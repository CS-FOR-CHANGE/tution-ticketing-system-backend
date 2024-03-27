from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Tutor, Student
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserRegistrationSerializer, TokenObtainPairSerializer, TutorSerializer, StudentSerializer
)
from django.contrib.auth import get_user_model
from django.http import JsonResponse


# Create your views here.
class UserDataView(APIView):
    # Get the Student or Tutor Data (As User)
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        tutor = Tutor.objects.filter(user=user).first()
        student = Student.objects.filter(user=user).first()

        if tutor:
            serializer = TutorSerializer(tutor)
        elif student:
            serializer = StudentSerializer(student)
        else:
            return Response({"error": "User is neither a Tutor nor a Student"}, status=404)

        return Response(serializer.data)


class TutorListView(APIView):
    # List all the tutors
    def get(self, request, format=None):
        return Response("serializer.data, status=status.HTTP_200_OK")


class UserRegistrationView(APIView):
    # Regester users
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()


class TutorTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Enhanced input validation for 'email'
        email = request.data.get('email', None)

        # Ensure 'email' is not only present but also a string
        if email and isinstance(email, str):
            user = User.objects.filter(email=email).first()

            # Conducting existence and role check
            if user is None or not Tutor.objects.filter(user=user).exists():
                # Returning a generic error message to avoid data leakage
                return JsonResponse({
                    'detail': 'Invalid credentials.'
                }, status=status.HTTP_404_NOT_FOUND)

        else:
            # Return an error if email is not provided or is not a string
            return JsonResponse({
                'detail': 'Invalid email format.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Proceeding with the original implementation if checks pass
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            organization = request.data.get('organization', None)
            # Assuming 'organization' is also validated if necessary
            user_role = 'tutor'  # Setting user role after verification

            # Safely adding extra information to the response
            response_data = response.data
            response_data['organization'] = organization
            response_data['user_role'] = user_role

            response.data = response_data

        return response


class StudentTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)

        # First, validate input to prevent injection attacks
        # Ensure email is a string to prevent type-related vulnerabilities
        if email and isinstance(email, str):
            # Clean or validate the email to prevent any form of injection or indirect attacks

            user = User.objects.filter(email=email).first()
            if user is None or not Student.objects.filter(user=user).exists():
                # If the user does not exist or is not a Student, return an error response
                return JsonResponse({
                    'detail': 'Student does not exist.'
                }, status=status.HTTP_404_NOT_FOUND)

        else:
            # If email is not provided or is invalid, return an error
            return JsonResponse({
                'detail': 'Invalid request, email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # If the checks pass, proceed with the original implementation
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            organization = request.data.get('organization', None)
            if organization and not isinstance(organization, str):
                # Log this issue, respond with an error or handle accordingly
                # It's crucial to ensure that the organization field, if present, is valid to prevent any issues
                organization = "Default Organization"  # or handle appropriately

            user_role = 'student'
            # Now, add the organization and user_role to the response data
            response.data['organization'] = organization
            response.data['user_role'] = user_role

        return response
