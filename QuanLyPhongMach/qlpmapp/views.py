import cloudinary.uploader
from django.contrib.auth.models import Group
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework import generics
from qlpmapp.models import Doctor, Nurse, Patient, Medicine, Schedule
from qlpmapp.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from qlpmapp.perms import *


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
            return Response({'success: Medicine created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]

# class AdminViewSet(viewsets.ViewSet):
#
#     def get_permissions(self):
#         permission_classes = [permissions.IsAdminUser]
#         return [permission() for permission in permission_classes]
#
#     def list_doctors(self, request):
#         queryset = Doctor.objects.all()
#         serializer = DoctorSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def create_doctor(self, request):
#         serializer = DoctorSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def update_doctor(self, request, pk=None):
#         doctor = Doctor.objects.get(pk=pk)
#         serializer = DoctorSerializer(doctor, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete_doctor(self, request, pk=None):
#         doctor = Doctor.objects.get(pk=pk)
#         doctor.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     # Tương tự cho Nurse, Medicine, Schedule
#
#     def list_nurses(self, request):
#         queryset = Nurse.objects.all()
#         serializer = NurseSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def create_nurse(self, request):
#         serializer = NurseSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     # Các phương thức khác tương tự cho bác sĩ, y tá, lịch trực, và thuốc
#
#     def list_patients(self, request):
#         queryset = Patient.objects.all()
#         serializer = PatientSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def create_patient(self, request):
#         serializer = PatientSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     # Các phương thức khác tương tự cho bệnh nhân

