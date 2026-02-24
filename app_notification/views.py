from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from app_notification import models, serializers
from app_notification.pagination import NotificationPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class NotificationListView(generics.ListAPIView):
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_read'] 
    def get_queryset(self):
        return (
            models.Notification.objects
            .filter(receiver=self.request.user)
            .select_related('sender', 'post')
            .order_by('-created_at') 
        )


class NotificationUnreadCount(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = models.Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        return Response({"unread_count": count})
    

class NotificationMarkAsRead(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        notification = generics.get_object_or_404(
            models.Notification,
            pk=pk,
            receiver=request.user
        )

        notification.is_read = True
        notification.save()

        return Response({"status": True, "message": "Marked as read"})
    

class NotificationMarkAllAsRead(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        updated_count = models.Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {
                "status": True,
                "updated_count": updated_count,
                "message": "All notifications marked as read"
            },
            status=status.HTTP_200_OK
        )