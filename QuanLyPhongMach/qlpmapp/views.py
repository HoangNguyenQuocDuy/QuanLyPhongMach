import cloudinary.uploader
from django.contrib.auth.models import Group
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework import generics
from qlpmapp.models import Doctor, Nurse, Patient, Medicine, Schedule, Appointment, User
from qlpmapp.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from qlpmapp.perms import *
from django.utils import timezone


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
            return Response({'success': f'{profile_type} created successfully',
                                'data': profile.data
                             }, status=status.HTTP_201_CREATED)
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
            # ...

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

