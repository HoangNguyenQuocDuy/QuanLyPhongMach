import cloudinary.uploader
from rest_framework import serializers
from .models import (Patient, Doctor, Nurse, Medicine, Schedule, Appointment,
                     Payment, MedicalHistory, User, Prescription, PrescribedMedicine, Statistics)


class UserDetailSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')
    gender = serializers.CharField()
    avatar = serializers.SerializerMethodField()
    birth = serializers.DateField()
    group_name = serializers.CharField(source='user.groups.first.name', allow_null=True)
    address = serializers.CharField()

    class Meta:
        fields = ['username', 'first_name', 'last_name', 'gender', 'avatar',
                  'birth', 'group_name', 'address', 'email']

    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'avatar']

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

    # def updatae(self, instance, validated_data):
    #     user_data = validated_data.pop('user', {})
    #     user = instance.user
    #
    #     if 'first_name' in user_data:
    #         user.first_name = user_data['first_name']
    #     if 'last_name' in user_data:
    #         user.last_name = user_data['last_name']
    #
    #     user.save()
    #
    #     instance.address = validated_data.get('address', instance.address)
    #     instance.birth = validated_data.get('birth', instance.birth)
    #     instance.gender = validated_data.get('gender', instance.gender)
    #     instance.faculty = validated_data.get('faculty', instance.faculty)
    #
    #     instance.save()
    #     return instnce


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'active_substances', 'price', 'unit', 'quantity',
                  'description', 'image', 'dosage', 'instructions', 'usage_instructions']

    def create(self, validated_data):
        image_url = None
        if 'image' in validated_data:
            uploaded_image = validated_data['image']
            cloudinary_folder = "Clinic"
            upload_result = cloudinary.uploader.upload(uploaded_image, folder=cloudinary_folder)
            image_url = upload_result.get('secure_url')

        validated_data['image'] = image_url
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            instance.name = validated_data['name']
        if 'active_substances' in validated_data:
            instance.active_substances = validated_data['image']
        if 'price' in validated_data:
            instance.price = validated_data['price']
        if 'unit' in validated_data:
            instance.unit = validated_data['unit']
        if 'quantity' in validated_data:
            instance.quantity = validated_data['quantity']
        if 'description' in validated_data:
            instance.description = validated_data['description']
        if 'dosage' in validated_data:
            instance.dosage = validated_data['dosage']
        if 'instructions' in validated_data:
            instance.instructions = validated_data['instructions']
        if 'usage_instructions' in validated_data:
            instance.usage_instructions = validated_data['usage_instructions']
        if 'image' in validated_data:
            uploaded_image = validated_data['image']
            cloudinary_folder = "Clinic"
            upload_result = cloudinary.uploader.upload(uploaded_image, folder=cloudinary_folder)
            image_url = upload_result.get('secure_url')
            instance.image = image_url

        instance.save()
        return instance


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'schedule_time', 'doctors', 'nurses', 'description']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'nurse', 'scheduled_time', 'reason', 'doctor',
                  'created_at', 'updated_at', 'confirmed', 'examination']


class PrescribedMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescribedMedicine
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'doctor', 'patient', 'symptoms', 'conclusion',
                  'prescribed_medicines', 'appointment', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()

    class Meta:
        model = Payment
        fields = '__all__'


class MedicalHistorySerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    doctor = DoctorSerializer()
    prescribed_medicines = PrescribedMedicineSerializer(many=True)

    class Meta:
        model = MedicalHistory
        fields = '__all__'


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ['month', 'quarter', 'year', 'patient_count', 'revenue']
