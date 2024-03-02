from django.urls import path, include
from rest_framework import routers
from qlpmapp import views

router = routers.DefaultRouter()
router.register('doctors', views.DoctorViewSet, basename='doctors')
router.register('medicines', views.MedicineViewSet, basename='medicines')
router.register('patients', views.PatientViewSet, basename='patients')
router.register('nurses', views.NurseViewSet, basename='nurses')
router.register('schedules', views.ScheduleViewSet, basename='schedules')
router.register('appointments', views.AppointmentViewSet, basename='appointments')
router.register('prescriptions', views.PrescriptionViewSet, basename='prescriptions')
router.register('medicalHistories', views.MedicalHistoryViewSet, basename='medicalHistories'),
router.register('payments', views.PaymentView, basename='payment'),
router.register('statistics', views.StatisticsViewSet, basename='statistics'),


urlpatterns = [
    path('', include(router.urls)),
    path('users/<str:username>/', views.GetUserByUsername.as_view(), name='get_user_by_username'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
]