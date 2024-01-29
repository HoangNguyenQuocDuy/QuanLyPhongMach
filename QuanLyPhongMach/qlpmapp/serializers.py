from rest_framework import serializers
from .models import Patient, Doctor, Nurse, Medicine, Appointment, Payment, MedicalHistory, User


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
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Patient
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'address', 'birth', 'avatar', 'gender', 'major')
        depth = 1


class DoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Doctor
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'gender', 'speciality')


class NurseSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Nurse
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'gender', 'faculty')


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


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
