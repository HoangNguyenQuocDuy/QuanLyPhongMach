import cloudinary.uploader
from rest_framework import serializers
from .models import Patient, Doctor, Nurse, Medicine, Schedule, Appointment, Payment, MedicalHistory, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'avatar']

    def create(self, validated_data):
        data = validated_data.copy()

        user = User(**data)
        user.set_password(user.password)
        user.save()
        return user


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'address', 'birth', 'gender', 'major']
        depth = 1


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'address', 'birth', 'gender', 'speciality']


class NurseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Nurse
        fields = ['id', 'user', 'address', 'birth', 'gender', 'faculty']


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'active_substances', 'price', 'unit', 'quantity', 'description', 'image']

    def create(self, validated_data):
        image_url = None
        if 'image' in validated_data:
            uploaded_image = validated_data['image']
            cloudinary_folder = "Clinic"
            upload_result = cloudinary.uploader.upload(uploaded_image, folder=cloudinary_folder)
            image_url = upload_result.get('secure_url')

        validated_data['image'] = image_url
        return super().create(validated_data)


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'schedule_time', 'doctors', 'nurses', 'description']
# class AppointmentSerializer(serializers.ModelSerializer):
#     patient = PatientSerializer()
#
#     class Meta:
#         model = Appointment
#         fields = '__all__'


# class PaymentSerializer(serializers.ModelSerializer):
#     patient = PatientSerializer()
#
#     class Meta:
#         model = Payment
#         fields = '__all__'


# class MedicalHistorySerializer(serializers.ModelSerializer):
#     patient = PatientSerializer()
#     doctor = DoctorSerializer()
#     prescribed_medicines = MedicineSerializer(many=True)
#
#     class Meta:
#         model = MedicalHistory
#         fields = '__all__'
