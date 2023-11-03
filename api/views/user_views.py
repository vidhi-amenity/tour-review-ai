from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from api.models import User, Company
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from api.serializers import (UserSerializer, 
                             UserCreateSerializer, 
                             UserUpdateSerializer)
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import UserFilter, CompanyFilter
from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class IsClientUser(permissions.BasePermission):
    """
    Allows access only to Client users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == User.CLIENT


class OwnRecordPermission(permissions.BasePermission):
    """
    Allow users to only see and edit their own details.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsClientUser]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    pagination_class = PageNumberPagination
    pagination_class.page_size = settings.REST_FRAMEWORK['PAGE_SIZE']

    def get_queryset(self):
        # User created by the admin
        if not self.request.user.created_by:
            return User.objects.filter(Q(id=self.request.user.id) | Q(created_by=self.request.user))
        else:
            # other users
            return User.objects.filter(Q(created_by=self.request.user.created_by) | Q(id=self.request.user.created_by.id))

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        if not self.request.user.created_by:
            return serializer.save(created_by=self.request.user)
        else:
            return serializer.save(created_by=self.request.user.created_by)

    def create(self, request, *args, **kwargs):
        user = request.user.created_by if request.user.created_by else request.user
        if User.objects.filter(created_by=user).count() >= 25:
            raise ValidationError({"message": "You have reached the limit of 25 users."})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        companies = Company.objects.filter(related_users=user)
        if companies.exists():
            company = companies.first()
            company.related_users.add(instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class UserPasswordResetView(APIView):
    permission_classes = [IsClientUser, OwnRecordPermission]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        password = request.data.get("new_password")
        if password:
            user.set_password(password)
            user.save()
            return Response({"message": "Password reset successfully."}, status=200)
        else:
            return Response({"message": "New password not provided."}, status=400)
