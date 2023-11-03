from .serializers import UserGetSerializer, UserPutSerializer, UserImageSerializer, CompanySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from .models import User, Company
import pyotp
from rest_framework import status, generics
import pytz
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from django.conf import settings


class UserDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request):
        user = request.user
        if user:
            serializer = UserGetSerializer(user)
            res = serializer.data
            companies = Company.objects.filter(related_users=user)
            if companies.exists():
                company = companies.first()
                res['company'] = CompanySerializer(company).data
                if res['company']['plan']:
                    res['company']['plan'] = dict(settings.PLAN_CHOICES)[res['company']['plan']]
            else:
                res['company'] = {
                    'is_subscription_active': request.user.is_superuser,
                    'subscription_ends': None,
                    'plan': "None"
                }
            return Response(res)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        user = request.user
        serializer = UserPutSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        timezone_name = request.data.get('timezone')
        if timezone_name is not None:
            if timezone_name not in pytz.all_timezones:
                return Response({'message': 'Invalid timezone name.'}, status=400)

        serializer.save()
        return Response(serializer.data)


class ProfileImageView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserImageSerializer

    def post(self, request):
        user = request.user
        print(user)
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
            user.save()
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            return Response({'error': 'profile_image missing'}, status=400)

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.profile_image:
            response = HttpResponse(user.profile_image, content_type='image/jpeg')
            response['Content-Disposition'] = 'inline; filename={}'.format(user.profile_image.name)
            return response
        else:
            return HttpResponseBadRequest('Profile image not found.', status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        totp_code = request.data.get('totp_code')

        username = User.objects.get(email=email.lower()).username
        print(username)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            # totp = pyotp.TOTP(user.totp_secret)
            # print(totp.verify(totp_code))
            # if totp.verify(totp_code):
            #     login(request, user)
            #
            #     refresh = RefreshToken.for_user(user)
            #     access = refresh.access_token
            #
            #     return Response({'access': str(access), 'refresh': str(refresh)}, status=200)

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            return Response({'access': str(access), 'refresh': str(refresh)}, status=200)

        return Response({'message': 'Invalid username, password, or TOTP code.'}, status=400)


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Check if the current password is correct
        if not user.check_password(current_password):
            return Response({"message": "The current password is incorrect."}, status=400)

        # Check if the new password matches the confirmation password
        if new_password != confirm_password:
            return Response({"message": "The new password and confirmation password do not match."}, status=400)

        # Hash the new password and set it for the user
        user.password = make_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully."}, status=200)

