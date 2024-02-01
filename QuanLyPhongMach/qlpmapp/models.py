from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import datetime
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True)


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    groups = models.ManyToManyField(Group, related_name='custom_users')
    birth = models.DateField(default=timezone.now)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    address = models.CharField(max_length=100, default='')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Patient(CustomUser):
    major = models.CharField(max_length=100)
    groups = models.ManyToManyField(Group, related_name='patient_groups')


class Administrator(CustomUser):
    groups = models.ManyToManyField(Group, related_name='admin_groups')
    pass


class Doctor(CustomUser):
    speciality = models.CharField(max_length=50)
    groups = models.ManyToManyField(Group, related_name='doctor_groups')

    def __str__(self):
        return f"{self.id}  - {self.gender} - {self.speciality}"


class Nurse(CustomUser):
    faculty = models.CharField(max_length=50)
    groups = models.ManyToManyField(Group, related_name='nurse_groups')

    def __str__(self):
        return f"{self.id} - {self.gender} - {self.faculty}"


class Schedule(models.Model):
    schedule_time = models.DateTimeField(default=timezone.now, null=False)
    doctors = models.ManyToManyField(Doctor, related_name='doctor_schedules', blank=True)
    nurses = models.ManyToManyField(Nurse, related_name='nurse_schedules', blank=True)
    description = models.TextField(default='')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active_substances = models.TextField(default='')
    unit = models.CharField(max_length=50, default=0)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(default='')
    image = CloudinaryField('medicine', null=True)
    dosage = models.CharField(max_length=50, null=True, blank=True)
    instructions = models.CharField(max_length=50, default='Drink')
    usage_instructions = models.CharField(max_length=100, default='')
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, null=True)
    scheduled_time = models.DateTimeField(default=datetime.now)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    confirmed = models.BooleanField(default=False)


class Payment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescription = models.OneToOneField('Prescription', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)


class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptoms = models.TextField()
    conclusion = models.TextField()
    prescribed_medicines = models.ManyToManyField(Medicine, through='PrescribedMedicine')
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"Prescription for {self.patient.name} by Dr. {self.doctor.name}"


class PrescribedMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    instructions = models.CharField(max_length=50, default='Drink')
    usage_instructions = models.CharField(max_length=50, default='')
    quantity = models.PositiveIntegerField(default=0)
    days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.medicine.name} - Days: {self.days} - Quantity: {self.quantity}"


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_history_doctor')
    symptoms = models.TextField()
    conclusion = models.TextField()
    prescribed_medicines = models.ManyToManyField(PrescribedMedicine, related_name='prescribed_medicines')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


# class Statistics(models.Model):
#     month = models.PositiveIntegerField()
#     quarter = models.PositiveIntegerField()
#     year = models.PositiveIntegerField()
#     patient_count = models.PositiveIntegerField(default=0)
#     revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
#
#     class Meta:
#         unique_together = ['month', 'quarter', 'year']
#
#     def __str__(self):
#         return f"{self.year}-{self.quarter}-{self.month}"


admin_group = Group.objects.get(name='Admin')
doctor_group = Group.objects.get(name='Doctor')
nurse_group = Group.objects.get(name='Nurse')
patient_group = Group.objects.get(name='Patient')

# user_doctor1 = User.objects.create_user(
#     username='example_user',  # Tên đăng nhập
#     email='example@example.com',  # Địa chỉ email
#     password='password123',  # Mật khẩu
#     first_name='John',  # Tên
#     last_name='Doe'  # Họ
# )
# doctor1 = Doctor.objects.create(
#     user=user_doctor1,
#     role=doctor_group,
#     birth='1990-01-01',
#     gender='male',
#     address='576 Nguyen Oanh, Go Vap, Ho Chi Minh city',
#     active=True,
#     speciality='Otorhinolaryngology'
# )
#
# admin_group.permissions.add(
#     # Doctor
#     Permission.objects.get(codename='add_doctor'),
#     Permission.objects.get(codename='change_doctor'),
#     Permission.objects.get(codename='delete_doctor'),
#     Permission.objects.get(codename='view_doctor'),
#
#     # Nurse
#     Permission.objects.get(codename='add_nurse'),
#     Permission.objects.get(codename='change_nurse'),
#     Permission.objects.get(codename='delete_nurse'),
#     Permission.objects.get(codename='view_nurse'),
#
#     # Medicine
#     Permission.objects.get(codename='add_medicine'),
#     Permission.objects.get(codename='change_medicine'),
#     Permission.objects.get(codename='delete_medicine'),
#     Permission.objects.get(codename='view_medicine'),
#
#     # Schedule
#     Permission.objects.get(codename='add_schedule'),
#     Permission.objects.get(codename='change_schedule'),
#     Permission.objects.get(codename='delete_schedule'),
#     Permission.objects.get(codename='view_schedule'),
#
#     # #Statistics
#     # Permission.objects.get(codename='add_statistics'),
#     # Permission.objects.get(codename='view_statistics'),
# )
#
# doctor_group.permissions.add(
#     Permission.objects.get(codename='add_prescription'),
#     Permission.objects.get(codename='change_prescription'),
#     Permission.objects.get(codename='add_prescribedMedicine'),
#     Permission.objects.get(codename='change_prescribedMedicine'),
#     Permission.objects.get(codename='view_medicalHistory'),
# )
#
# nurse_group.permissions.add(
#     Permission.objects.get(codename='change_appointment'),
# )
#
# patient_group.permissions.add(
#     Permission.objects.get(codename='add_appointment'),
#     Permission.objects.get(codename='delete_appointment'),
# )
