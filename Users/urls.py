from django.urls import path
from .views import (
    UserDataView, TutorListView, UserRegistrationView,
    TutorTokenObtainPairView, StudentTokenObtainPairView,
    LogoutAPIView, ProfileUpdateAPIView
)

urlpatterns = [
    path('user/', UserDataView.as_view(), name='user-data'),
    path('users/tutors/', TutorListView.as_view(), name='subject-list'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/tutor/', TutorTokenObtainPairView.as_view(),
         name='tutor_token_obtain_pair'),
    path('token/student/', StudentTokenObtainPairView.as_view(),
         name='student_token_obtain_pair'),
    path('user/logout/', LogoutAPIView.as_view(), name='logout'),
    path('user/update-profile/', ProfileUpdateAPIView.as_view(),
         name='update_profile'),
]
