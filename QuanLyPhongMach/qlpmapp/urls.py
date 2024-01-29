from django.urls import path, include
from rest_framework import routers
from qlpmapp import views

router = routers.DefaultRouter()
router.register('doctors', views.DoctorViewSet, basename='doctors')
router.register('medicine', views.MedicineViewSet, basename='medicine')
router.register('patients', views.PatientViewSet, basename='patients')


urlpatterns = [
    path('', include(router.urls))
]