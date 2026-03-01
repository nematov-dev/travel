from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import ChatMessage, ChatMedia, MessageReaction

class ChatMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMedia
        fields = ['id', 'file', 'file_type']

class ReactionInputSerializer(serializers.Serializer):
    emoji = serializers.CharField(max_length=10, help_text="Send an emoji to react to the message. Example: '👍'")

class MessageReactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = MessageReaction
        fields = ['user', 'user_email', 'emoji']

@extend_schema_field({"type": "array", "items": {"type": "string", "format": "binary"}})
class MultipleImageField(serializers.ListField):
    child = serializers.ImageField()

class ChatMessageSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    medias = ChatMediaSerializer(many=True, read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    
    parent_text = serializers.CharField(source='parent.text', read_only=True)
    
    uploaded_images = MultipleImageField(write_only=True, required=False)

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'user', 'user_email', 'text', 'parent', 'parent_text',
            'medias', 'uploaded_images', 'reactions', 'replies_count', 'created_at'
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        validated_data['user'] = self.context['request'].user
        message = ChatMessage.objects.create(**validated_data)
        
        for image in images_data:
            ChatMedia.objects.create(message=message, file=image, file_type='image')
        return message