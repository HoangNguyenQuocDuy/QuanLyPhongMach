import cloudinary.uploader
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework import generics
from qlpmapp.models import Doctor, Nurse, Patient, Medicine, Schedule, Appointment, User, Prescription, \
    PrescribedMedicine
from qlpmapp.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from qlpmapp.perms import *
from django.utils import timezone
from QuanLyPhongMach import settings


def create_user_and_profile(request, profile_type):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():

        avatar_url = None
        if 'avatar' in request.data:
            uploaded_file = request.data['avatar']
            cloudinary_folder = "Clinic"
            upload_result = cloudinary.uploader.upload(uploaded_file, folder=cloudinary_folder)
            avatar_url = upload_result.get('secure_url')

        user_data = {
            'username': request.data['username'],
            'email': request.data['email'],
            'password': request.data['password'],
            'first_name': request.data['first_name'],
            'last_name': request.data['last_name'],
            'avatar': avatar_url
        }

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            profile_data = {
                'user': user_serializer.instance,
                'gender': request.data['gender'],
                'address': request.data['address'],
                'birth': request.data['birth'],
            }
            if profile_type == 'Doctor':
                profile_data['speciality'] = request.data['speciality']
                profile = Doctor.objects.create(**profile_data)

            elif profile_type == 'Patient':
                profile_data['major'] = request.data['major']
                profile = Patient.objects.create(**profile_data)

            elif profile_type == 'Nurse':
                profile_data['faculty'] = request.data['faculty']
                profile = Nurse.objects.create(**profile_data)

            profile.groups.add(Group.objects.get(name=profile_type))

            profile.save()
            return Response({'success': f'{profile_type} created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]

    def create(self, request, *args, **kwargs):
        return create_user_and_profile(request, 'Doctor')


class PatientViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    # authentication_classes = [OAuth2Authentication]
    def create(self, request):
        return create_user_and_profile(request, 'Patient')


class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]

    def create(self, request, *args, **kwargs):
        return create_user_and_profile(request, 'Nurse')


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]

    def create(self, request, *args, **kwargs):
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Medicine created successfully',
                             'data': serializer.data
                             }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]


class AppointmentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                         generics.UpdateAPIView, generics.DestroyAPIView,
                         generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not (PatientPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()
        total_appointments_today = Appointment.objects.filter(scheduled_time__date=today).count()
        if total_appointments_today >= 100:
            return Response({'error': 'Maximum appointments for today exceeded'}, status=status.HTTP_403_FORBIDDEN)

        serializer_data = {
            'scheduled_time': request.data['scheduled_time'],
            'patient': Patient.objects.get(user=request.user).id
        }
        print('patient: ', Patient.objects.get(user=request.user).id)

        serializer = AppointmentSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Appointment created successfully',
                             'data': serializer.data
                             }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if not (NursePermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            nurse = Nurse.objects.get(user=request.user)

            serializer.validated_data['nurse'] = nurse
            serializer.save()

            # Gửi email
            subject = 'DC CLINIC - APPOINTMENT CONFIRMATION'
            message = f"Your appointment at {instance.scheduled_time} has been confirmed."
            from_email = settings.EMAIL_HOST_USER
            to_email = instance.patient.user.email

            send_mail(subject, message, from_email, [to_email], fail_silently=True)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not (PatientPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        user = request.user

        if instance.patient.user != user:
            return Response({'error': 'You are not authorized to delete this appointment'},
                            status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response({'success': 'Appointment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        if not (Nurse.objects.filter(user=request.user) or Patient.objects.filter(user=request.user)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if Nurse.objects.filter(user=request.user):
            queryset = Appointment.objects.filter(confirmed=False)
        else:
            queryset = Appointment.objects.filter(patient__user=request.user)

        serializer = AppointmentSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if not (NursePermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        serializer = AppointmentSerializer(instance)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not (DoctorPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        doctor = request.user.doctor
        patient_id = request.data['patient']
        symptoms = request.data['symptoms']
        conclusion = request.data['conclusion']
        prescribed_medicines = request.data['prescribed_medicines']

        appointment = Appointment.objects.get(pk=request.data['appointment'])
        if appointment.doctor is not None:
            return Response({'error': 'Doctor already assigned to this appointment'},
                            status=status.HTTP_400_BAD_REQUEST)

        prescription = Prescription.objects.create(doctor=doctor, patient_id=patient_id, symptoms=symptoms,
                                                   conclusion=conclusion)

        medical_history = MedicalHistory.objects.create(
            patient_id=patient_id,
            doctor=doctor,
            appointment=appointment,
            symptoms=symptoms,
            conclusion=conclusion,
        )

        for medicine_data in prescribed_medicines:
            medicine_id = medicine_data['medicine']

            try:
                medicine = Medicine.objects.get(id=medicine_id)
            except Medicine.DoesNotExist:
                return Response({'error': f'Medicine with ID {medicine_id} does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)

            instructions = medicine_data.get('instructions', medicine.instructions)
            usage_instructions = medicine_data.get('usage_instructions', medicine.usage_instructions)
            quantity = medicine_data['quantity']
            days = medicine_data['days']

            prescribed_medicine = PrescribedMedicine.objects.create(
                prescription=prescription,
                medicine=medicine,
                instructions=instructions,
                quantity=quantity,
                days=days,
                usage_instructions=usage_instructions
            )
            medical_history.prescribed_medicines.add(prescribed_medicine)

        appointment.doctor = doctor
        appointment.save()

        serializer = PrescriptionSerializer(prescription)
        return Response({'success': 'Prescription created successfully',
                         'data': serializer.data
                         }, status=status.HTTP_201_CREATED)


class MedicalHistoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Prescription.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, DoctorPermissions]

    def list(self, request, *args, **kwargs):
        patient_id = request.query_params.get('p_id', None)

        if patient_id is None:
            return Response({'error': 'Parameter "p_id" is required'}, status=status.HTTP_400_BAD_REQUEST)

        medical_history = MedicalHistory.objects.filter(patient_id=patient_id)

        serializer = MedicalHistorySerializer(medical_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
