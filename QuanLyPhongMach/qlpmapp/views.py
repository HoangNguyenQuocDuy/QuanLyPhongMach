from datetime import datetime
from decimal import Decimal

import cloudinary.uploader
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Sum, DecimalField, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.timezone import make_aware
from rest_framework import viewsets, status, permissions
from rest_framework import generics
from qlpmapp.models import Doctor, Nurse, Patient, Medicine, Schedule, Appointment, User, Prescription, \
    PrescribedMedicine, Statistics, Administrator, Payment, MedicalHistory
from qlpmapp.serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from qlpmapp.perms import *
from django.utils import timezone
from rest_framework.views import APIView
from setuptools.command.install import install
from qlpmapp.paginators import CustomPageNumberPagination
from django.db.models import F

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
            return Response({'success': f'{profile_type} created successfully',
                             'data': { 'id': profile.id }}, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not (AdminPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return create_user_and_profile(request, 'Doctor')

    def update(self, request, *args, **kwargs):
        if not (AdminPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        user_instance = instance.user

        if 'avatar' in request.data:
            uploaded_file = request.data['avatar']
            cloudinary_folder = "Clinic"
            upload_result = cloudinary.uploader.upload(uploaded_file, folder=cloudinary_folder)
            avatar_url = upload_result.get('secure_url')
            user_instance.avatar = avatar_url
        if 'first_name' in request.data:
            user_instance.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user_instance.last_name = request.data['last_name']
        if 'address' in request.data:
            instance.address = request.data['address']
        if 'birth' in request.data:
            instance.birth = request.data['birth']
        if 'gender' in request.data:
            instance.gender = request.data['gender']
        if 'speciality' in request.data:
            instance.faculty = request.data['speciality']

        user_instance.save()
        instance.save()

        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = Doctor.objects.all()
        name = request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(user__first_name__icontains=name) | queryset.filter(
                user__last_name__icontains=name)

        serializer = DoctorSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not (AdminPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = self.get_object()
            user_instance = instance.user
            self.perform_destroy(instance)
            user_instance.delete()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    pagination_class = CustomPageNumberPagination
    # authentication_classes = [OAuth2Authentication]

    def list(self, request, *args, **kwargs):
        queryset = Patient.objects.all()
        name = request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(user__first_name__icontains=name) | queryset.filter(
                user__last_name__icontains=name)

        page = self.paginate_queryset(queryset)
        serializer = PatientSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        return create_user_and_profile(request, 'Patient')

    def retrieve(self, request, pk=None):
        try:
            patient = Patient.objects.get(pk=pk)
            serializer = PatientSerializer(patient)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response('Patient not found', status=status.HTTP_404_NOT_FOUND)


class NurseViewSet(viewsets.ModelViewSet):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]

    def create(self, request, *args, **kwargs):
        return create_user_and_profile(request, 'Nurse')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user_instance = instance.user

        if 'avatar' in request.data:
            uploaded_file = request.data['avatar']
            cloudinary_folder = "Clinic"
            upload_result = cloudinary.uploader.upload(uploaded_file, folder=cloudinary_folder)
            avatar_url = upload_result.get('secure_url')
            user_instance.avatar = avatar_url
        if 'first_name' in request.data:
            user_instance.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user_instance.last_name = request.data['last_name']
        if 'address' in request.data:
            instance.address = request.data['address']
        if 'birth' in request.data:
            instance.birth = request.data['birth']
        if 'gender' in request.data:
            instance.gender = request.data['gender']
        if 'faculty' in request.data:
            instance.faculty = request.data['faculty']

        user_instance.save()
        instance.save()

        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = Nurse.objects.all()
        name = request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(user__first_name__icontains=name) | queryset.filter(
                user__last_name__icontains=name)

        serializer = NurseSerializer(queryset, many=True)
        return Response(serializer.data)


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def create(self, request, *args, **kwargs):
        if AdminPermissions.has_permission(self, request, MedicineViewSet):
            serializer = MedicineSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response( serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        try:
            if PatientPermissions.has_permission(self, request, MedicineViewSet):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except PermissionDenied:
            queryset = Medicine.objects.all()
            name = request.query_params.get('name', None)

            if name:
                queryset = queryset.filter(name__icontains=name)
            page = self.paginate_queryset(queryset)
            serializer = MedicineSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        if AdminPermissions.has_permission(self, request, MedicineViewSet):
            serializer = MedicineSerializer(data=request.data)
            instance = self.get_object()

            serializer = MedicineSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = Schedule.objects.all()
        date = request.query_params.get('date', None)

        if date:
            queryset = queryset.filter(schedule_time__icontains=date)
        page = self.paginate_queryset(queryset)
        serializer = ScheduleSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        if AdminPermissions().has_permission(request, self):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        if AdminPermissions().has_permission(request, self):
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if AdminPermissions().has_permission(request, self):
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)


class AppointmentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                         generics.UpdateAPIView, generics.DestroyAPIView,
                         generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def create(self, request, *args, **kwargs):
        if not (PatientPermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()
        total_appointments_today = Appointment.objects.filter(scheduled_time__date=today).count()
        if total_appointments_today > 100:
            return Response({'error': 'Maximum appointments for today exceeded'}, status=status.HTTP_403_FORBIDDEN)

        serializer_data = {
            'scheduled_time': request.data['scheduled_time'],
            'reason': request.data['reason'],
            'patient': Patient.objects.get(user=request.user).id
        }
        print('patient: ', Patient.objects.get(user=request.user).id)

        serializer = AppointmentSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # if not (NursePermissions().has_permission(request, self)):
        #     return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            if Nurse.objects.filter(user=request.user).exists():
                nurse = Nurse.objects.get(user=request.user)
                doctor = Doctor.objects.get(pk=request.data['doctor'])

                serializer.validated_data['nurse'] = nurse
                serializer.validated_data['doctor'] = doctor
                serializer.save()

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
        date = request.query_params.get('date', None)
        if Patient.objects.filter(user=request.user).exists():
            queryset = Appointment.objects.filter(patient__user=request.user)
        elif Nurse.objects.filter(user=request.user).exists():
            queryset = Appointment.objects.filter(confirmed=False)
        else:
            queryset = Appointment.objects.filter(doctor__user=request.user, examination=False)

        if date:
            queryset = queryset.filter(scheduled_time__icontains=date)

        page = self.paginate_queryset(queryset)
        serializer = AppointmentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if not (NursePermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        serializer = AppointmentSerializer(instance)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
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
        # if appointment.doctor is not None:
        #     return Response({'error': 'Doctor already assigned to this appointment'},
        #                     status=status.HTTP_400_BAD_REQUEST)

        prescription = Prescription.objects.create(doctor=doctor, patient_id=patient_id, symptoms=symptoms,
                                                   conclusion=conclusion, appointment=appointment)

        medical_history = MedicalHistory.objects.create(
            patient_id=patient_id,
            doctor=doctor,
            appointment=appointment,
            symptoms=symptoms,
            conclusion=conclusion,
        )

        for medicine_data in prescribed_medicines:
            medicine_id = medicine_data['medicine']
            quantity = medicine_data['quantity']

            try:
                medicine = Medicine.objects.get(id=medicine_id)
            except Medicine.DoesNotExist:
                return Response({'error': f'Medicine with ID {medicine_id} does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)

            if medicine.quantity < quantity:
                return Response({'error': f'Not enough quantity for Medicine {medicine_id}'},
                                status=status.HTTP_400_BAD_REQUEST)

            medicine.quantity -= quantity
            medicine.save()

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

        appointment.examination = True
        appointment.save()

        payment = Payment.objects.create(patient_id=patient_id, prescription=prescription, fee=0, total=0,
                                         payment_method='')

        statistics, created = Statistics.objects.get_or_create(
            year=appointment.scheduled_time.year,
            quarter=(appointment.scheduled_time.month - 1) // 3 + 1,
            month=appointment.scheduled_time.month
        )
        statistics.patient_count += 1
        statistics.save()

        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        date = request.query_params.get('date', None)
        patient_id = request.query_params.get('patient_id', None)

        if Patient.objects.filter(user=request.user).exists():
            queryset = Prescription.objects.filter(patient__user=request.user)
        else:
            queryset = Prescription.objects.all()

        if date:
            queryset = queryset.filter(created_at__date=date)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        page = self.paginate_queryset(queryset)
        serializer = PrescriptionSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class MedicalHistoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Prescription.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, DoctorPermissions]
    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        patient_id = request.query_params.get('p_id', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if patient_id is None:
            return Response({'error': 'Parameter "p_id" is required'}, status=status.HTTP_400_BAD_REQUEST)

        if start_date is None or end_date is None:
            return Response({'error': 'Parameters "start_date" and "end_date" are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        medical_history = MedicalHistory.objects.filter(patient_id=patient_id, created_at__range=[start_date, end_date])

        page = self.paginate_queryset(medical_history)
        serializer = MedicalHistorySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class PaymentView(viewsets.ViewSet, generics.UpdateAPIView, generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def update(self, request, *args, **kwargs):
        if not (NursePermissions().has_permission(request, self)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            prescribed_medicines = instance.prescription.prescribed_medicines.all()
            total_amount = sum(medicine.price * medicine.quantity for medicine in prescribed_medicines)
            fee = request.data['fee']

            serializer.validated_data['fee'] = fee
            serializer.validated_data['total'] = total_amount + fee
            serializer.validated_data['nurse'] = Nurse.objects.get(user=request.user)
            serializer.validated_data['payment_method'] = request.data['payment_method']

            serializer.save()

            appointment_id = instance.prescription.appointment_id
            appointment = Appointment.objects.get(pk=appointment_id)
            statistics, _ = Statistics.objects.get_or_create(
                year=appointment.scheduled_time.year,
                quarter=(appointment.scheduled_time.month - 1) // 3 + 1,
                month=appointment.scheduled_time.month
            )
            statistics.revenue += total_amount
            statistics.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        date = request.query_params.get('date', None)
        patient_id = request.query_params.get('patient_id', None)

        if Nurse.objects.filter(user=request.user).exists():
            queryset = Payment.objects.filter(nurse=None)
        else:
            queryset = Payment.objects.all(patient__user=request.user)

        if date:
            queryset = queryset.filter(created_at__icontains=date)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        page = self.paginate_queryset(queryset)
        serializer = PaymentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class StatisticsViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [IsAuthenticated, AdminPermissions]

    def list(self, request, *args, **kwargs):
        start_month = request.query_params.get('startMonth')
        end_month = request.query_params.get('endMonth')
        start_quarter = request.query_params.get('startQuarter')
        end_quarter = request.query_params.get('endQuarter')
        start_year = request.query_params.get('startYear')
        end_year = request.query_params.get('endYear')

        statistics_list = []

        if start_month and end_month and start_year:
            monthly_statistics = Statistics.objects.filter(year=start_year, month__gte=start_month,
                                                           month__lte=end_month)
            statistics_list.extend(monthly_statistics)
        elif start_quarter and end_quarter and start_year:
            quarterly_statistics = Statistics.objects.filter(year=start_year, quarter__gte=start_quarter,
                                                             quarter__lte=end_quarter)
            quarterly_statistics = quarterly_statistics.values('year', 'quarter').annotate(
                total_patient_count=Sum('patient_count'),
                total_revenue=Sum('revenue')
            )

            return Response(quarterly_statistics)
        elif start_year and end_year:
            yearly_statistics = Statistics.objects.filter(year__gte=start_year, year__lte=end_year)
            yearly_statistics = yearly_statistics.values('year').annotate(
                total_patient_count=Sum('patient_count'),
                total_revenue=Sum('revenue')
            )
            return Response(yearly_statistics)

        serialized_data = StatisticsSerializer(statistics_list, many=True).data
        return Response(serialized_data)


class GetUserByUsername(APIView):
    def get(self, request, username):
        user = None
        user_types = [Patient, Administrator, Doctor, Nurse]
        for user_type in user_types:
            user = user_type.objects.filter(user__username=username).first()
            if user:
                break

        if user:
            group_name = user.groups.first().name if user.groups.exists() else None
            serializer = UserDetailSerializer(user)
            data = serializer.data
            data['group_name'] = group_name
            return Response(data)
        else:
            return Response({'error': 'User not found'}, status=404)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)

        token = get_random_string(length=6)

        user.reset_password_token = token
        user.save()

        subject = 'Password Reset Request'
        message = f"reset password: 'user': {user}, 'token': {token}"

        from_email = settings.EMAIL_HOST_USER
        to_email = [email]

        send_mail(subject, message, from_email, to_email)

        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        user = get_object_or_404(User, email=email)

        if user.reset_password_token == token:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)