from django.contrib import admin
from .models import (Doctor, Nurse, Patient, Medicine, Appointment, Payment,
                     MedicalHistory, Schedule, Prescription, PrescribedMedicine)
# Register your models here.


class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender', 'birth', 'address', 'speciality', 'active']


class NurseAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender', 'birth', 'address', 'faculty', 'active']


class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender', 'birth', 'address', 'major', 'active']


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Nurse, NurseAdmin)
admin.site.register(Medicine)
admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(MedicalHistory)
admin.site.register(Schedule)
admin.site.register(Prescription)
admin.site.register(PrescribedMedicine)
