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
router.register('medicalHistories', views.MedicalHistoryViewSet, basename='medicalHistories')


urlpatterns = [
    path('', include(router.urls))
]