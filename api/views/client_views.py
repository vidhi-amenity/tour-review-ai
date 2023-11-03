from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from api.models import User, Company
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (ClientSerializer, 
                             ClientCreateSerializer, 
                             ClientUpdateSerializer)
from rest_framework.permissions import BasePermission
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import UserFilter, CompanyFilter

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.utils.timezone import now
from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(role=User.CLIENT)
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    pagination_class = PageNumberPagination
    pagination_class.page_size = settings.REST_FRAMEWORK['PAGE_SIZE']

    def get_queryset(self):
        qs = super().get_queryset()
        company_filter = CompanyFilter(self.request.GET, queryset=Company.objects.filter(related_users__in=qs))
        filtered_companies = company_filter.qs
        return qs.filter(related_users__in=filtered_companies)

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClientUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        return serializer.save(role=User.CLIENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        company = Company.objects.create()
        company.related_users.add(instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def destroy(self, request, *args, **kwargs):
        client = self.get_object()
        User.objects.filter(created_by=client).delete()
        client.delete()  # This will delete the client completely
        return Response(status=status.HTTP_204_NO_CONTENT)

class IsUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return True  # Allow any authenticated user

    def has_object_permission(self, request, view, obj):
        # Allow if user is admin or if the user is updating their own password
        return request.user.is_staff or request.user == obj or request.user == User.CLIENT



class ClientPasswordResetView(APIView):
    permission_classes = [IsUserOrAdmin]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # Check if the request user is the one whose password is being changed or is an admin
        if (request.user != user and not request.user.is_staff) and request.user.role == User.USER :
            return Response({"message": "You can only reset your own password or you should be an admin."}, status=403)
        
        password = request.data.get("new_password")
        if password:
            user.set_password(password)
            user.save()
            return Response({"message": "Password reset successfully."}, status=200)
        else:
            return Response({"message": "New password not provided."}, status=400)

