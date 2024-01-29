import cloudinary.uploader
from django.contrib.auth.models import Group
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import generics
from qlpmapp.models import Doctor, Nurse, Patient, Medicine
from qlpmapp.serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView


class DoctorViewSet(viewsets.ViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class MedicineViewSet(viewsets.ViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer


class PatientViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    # authentication_classes = [OAuth2Authentication]
    def create(self, request):
        serializer = PatientSerializer(data=request.data)
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
                patient = Patient.objects.create(
                    user=user_serializer.instance,
                    gender=request.data['gender'],
                    major=request.data['major'],
                    role=Group.objects.get(name='Patient'),
                    address=request.data['address'],
                    birth=request.data['birth'],
                )
                patient.save()
                return Response({'success': 'Patient created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def login(self, request):
    #     # Xử lý logic đăng nhập ở đây
    #     pass

# class RegisterView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
