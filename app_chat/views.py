from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from .models import ChatMessage, MessageReaction
from .serializers import ChatMessageSerializer,ReactionInputSerializer
from .permissions import IsOwnerOrAdmin


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().prefetch_related('medias', 'reactions').order_by('-created_at')
    serializer_class = ChatMessageSerializer 
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        if self.action == 'react':
            return ReactionInputSerializer
        return ChatMessageSerializer

    @extend_schema(request={'multipart/form-data': ChatMessageSerializer})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        message = self.get_object()
        serializer = ReactionInputSerializer(data=request.data)
        
        if serializer.is_valid():
            emoji = serializer.validated_data['emoji']
            MessageReaction.objects.update_or_create(
                message=message, user=request.user,
                defaults={'emoji': emoji}
            )
            return Response({'status': 'Reaction set', 'emoji': emoji}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)