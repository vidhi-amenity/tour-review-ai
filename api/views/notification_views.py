from rest_framework import viewsets, generics,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from authentication.models import User
from api.models import Notification
from api.serializers import NotificationSerializer
from rest_framework import exceptions

class CreatedByPermission(permissions.BasePermission):
    """
    Object-level permission to only allow users to access objects created by them or by their creator.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow reading the object, not modifying it
            # Check if the user is the creator of the object
        if request.user == obj.client_field:
            return True

        # Check if the user has the same creator as the object
        elif (request.user.created_by == obj.client_field):
            return True

        return False


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, CreatedByPermission]

    def get_queryset(self):
        # Filters the notifications by the client of the user
        queryset = self.queryset.filter(read=False, client_field=self.request.user.created_by if self.request.user.role == User.USER else self.request.user)
        return queryset.order_by('-datetime')  # orders notifications by datetime in descending order

    @action(detail=True, methods=['post'])
    def set_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'Notification set to read'})


class CreateNotificationView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, client_field=self.request.user.created_by)
        else:
            raise exceptions.NotAuthenticated("User must be logged in to create a notification.")


class UpdateNotificationView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class DeleteNotificationView(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
