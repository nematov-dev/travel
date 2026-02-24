from rest_framework import serializers
from app_notification import models


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(
        source='sender.get_full_name',
        read_only=True
    )
    sender_avatar = serializers.SerializerMethodField()
    post_id = serializers.IntegerField(source='post.id', read_only=True)

    class Meta:
        model = models.Notification
        fields = [
            'id',
            'sender',
            'sender_name',
            'sender_avatar',
            'post_id',
            'notification_type',
            'is_read',
            'created_at'
        ]

    def get_sender_avatar(self, obj):
        if obj.sender.avatar:
            return obj.sender.avatar.url
        return None