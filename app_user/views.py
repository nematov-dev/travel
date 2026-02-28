import random
import threading
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions,filters,generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from app_notification.models import Notification

from app_user.serializers import EmailRegisterSerializer,EmailConfirmSerializer,UserRegisterSerializer,UserSerializer
from app_user import serializers
from app_user.utils import send_email_code
from app_user import models
from app_user import pagination
from app_user.utils_geo import is_ip_from_uz


User = get_user_model()

channel_layer = get_channel_layer()

class EmailRegister(APIView):
    @swagger_auto_schema(
        request_body=EmailRegisterSerializer,
        operation_description="""
        Accepts an email from the user and sends a verification code.
        The code is stored in cache for 5 minutes.
        Email sending runs in a background thread.
        """
    )
    
    def post(self, request):
        # 1️⃣ Check if IP is from Uzbekistan
        if not is_ip_from_uz(request):
            return Response(
                {"status": False, "message": "Registration is allowed only from Uzbekistan."},
                status=status.HTTP_403_FORBIDDEN
        )
        serializer = EmailRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        # 4-digit code
        code = random.randint(1000, 9999)
        # Save to cache for 5 minutes (300 seconds)
        cache.set(f'otp_{email}', code, timeout=300)

        # Run email sending in the background
        th = threading.Thread(target=send_email_code, args=(email, code))
        th.start()

        return Response({'status':True,'message': 'Code sent to email!'}, status=status.HTTP_200_OK)

class EmailConfirm(APIView):
    @swagger_auto_schema(
        request_body=EmailConfirmSerializer,
        operation_description="""
        Accepts an email and a verification code.
        Confirms the email if the code is correct.
        A special code '11111' can be used for testing.
        """
    )
    def post(self,request):
        serializer = EmailConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        real_code = cache.get(f'otp_{email}')

        if str(code) == str(real_code) or str(code) == "11111":
            cache.set(f'confirm_{email}', True, timeout=300)
            return Response({'status':True,'message': 'Email confirmed! You can register now!'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False,'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

class UserRegister(APIView):
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        request_body=UserRegisterSerializer,
        operation_description="""
        Registers a new user if the email has been confirmed.
        Supports multipart/form-data (for profile images and files).
        """
    )
    def post(self,request):
        # 1️⃣ Check if IP is from Uzbekistan
        if not is_ip_from_uz(request):
            return Response(
                {"status": False, "message": "Registration is allowed only from Uzbekistan."},
                status=status.HTTP_403_FORBIDDEN
        )
        serilizer = UserRegisterSerializer(data=request.data)
        if serilizer.is_valid(raise_exception=True):
            email = serilizer.validated_data['email']
            result = cache.get(f"confirm_{email}")
            if result:
                serilizer.save(is_user=True)
                return Response({'status':True,'message': 'Registered successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({"status":False,"message":"Email not confirmed."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status':False,'message':serilizer.errors},status=status.HTTP_400_BAD_REQUEST)



class AllPublicPostsList(generics.ListAPIView):
    """
    Shows only posts with is_status=True (public).
    Ordered by number of likes.
    Pagination default 10 posts per page.
    """
    serializer_class = serializers.UserPostDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location_name']
    ordering_fields = ['likes_count', 'id']
    ordering = ['-likes_count']  # most liked first

    def get_queryset(self):
        # Only public posts
        queryset = (
            models.UserPost.objects
            .filter(is_status=True)
            .annotate(likes_count=Count('likes'))
            .select_related('user', 'tag')
            .prefetch_related('medias', 'likes')
            .order_by('-likes_count', '-id')
        )
        return queryset



class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="""
        Allows the authenticated user to update their profile information.
        Partial updates are supported.
        """
    )
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Profile updated!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": False,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="""
        Returns the authenticated user's profile information.
        User is identified via JWT token.
        """
    )
    def get(self, request):
        user = request.user  # get user via JWT token
        serializer = UserSerializer(user)
        return Response({
            "data": serializer.data
        }, status=status.HTTP_200_OK)
 
class UserPost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('tag', openapi.IN_FORM, type=openapi.TYPE_INTEGER),
            openapi.Parameter('location_name', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('latitude', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('longitude', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('is_status', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('images', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description="Upload multiple images (Postman supports multiple files)"),
        ],
        consumes=['multipart/form-data'],
        responses={201: 'Post created successfully', 400: 'Bad request'},
        operation_description="""
        Creates a new post for the authenticated user.
        Supports multiple images and optional location information.
        """
    )

    def post(self, request):
        serializer = serializers.UserPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save()

            return Response({'status': True, 'message': 'Post created!'}, status=status.HTTP_201_CREATED)

        return Response({'status': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserPostGet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="""
        Retrieves all posts created by the authenticated user.
        Includes related tag and media information.
        """
    )
    def get(self, request):
        user = request.user
        posts = (
            models.UserPost.objects
            .filter(user=user)
            .select_related("user", "tag")
            .prefetch_related("medias", "likes")
            .order_by("-id")
        )
        serializer = serializers.UserPostDetailSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPostUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.UserPost.objects.all()
    lookup_url_kwarg = "post_id"

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return serializers.UserPostSerializer  # write
        return serializers.UserPostDetailSerializer  # read

    def perform_update(self, serializer):
        post = self.get_object()

        if post.user != self.request.user:
            raise PermissionDenied("You can't edit this post.")

        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request} 
        )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.refresh_from_db()

        read_serializer = serializers.UserPostDetailSerializer(instance)
        return Response(read_serializer.data)
    


class UserPostDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, post_id):
        post = get_object_or_404(models.UserPost, id=post_id)

        if post.user != request.user:
            return Response(
                {"status": False, "message": "You can't delete this post."},
                status=403
            )

        post.delete()
        return Response(
            {"status": True, "message": "Post deleted!"},
            status=200
        )


class AllPostsList(APIView):
    permission_classes = [permissions.AllowAny]  # accessible for unauthenticated users
    filter_backends = [filters.SearchFilter, filters.OrderingFilter,]
    @swagger_auto_schema(
        operation_description="""
        Retrieves all posts with like counts.
        Orders posts by number of likes in descending order.
        Accessible for both authenticated and unauthenticated users.
        """
    )
    def get(self, request):
        # Count likes for each post
        posts = (
            models.UserPost.objects
            .annotate(likes_count=Count('likes'))  # count likes
            .prefetch_related('medias', 'likes', 'tag', 'user')
            .order_by('-likes_count', '-id')  # most liked first
        )

        serializer = serializers.UserPostDetailSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostCommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=serializers.PostCommentSerializer)
    def post(self, request, post_id):
        post = get_object_or_404(models.UserPost, id=post_id)
        serializer = serializers.PostCommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(user=request.user, post=post)

            # 🔥 O‘z postiga comment qilsa notification yubormaymiz
            if post.user != request.user:

                # 1️⃣ DB ga yozish
                Notification.objects.create(
                    sender=request.user,
                    receiver=post.user,
                    post=post,
                    notification_type="comment"
                )

                # # 2️⃣ WebSocket orqali yuborish

                # async_to_sync(channel_layer.group_send)(
                #     f"user_{post.user.id}",
                #     {
                #         "type": "send_notification",
                #         "data": {
                #             "type": "comment",
                #             "message": f"{request.user.username} commented on your post",
                #             "post_id": post.id,
                #             "comment_id": comment.id
                #         }
                #     }
                # )

            return Response(
                {"status": True, "message": "Comment added!"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)


class PostCommentListView(generics.ListAPIView):
    serializer_class = serializers.PostCommentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = pagination.DefaultPagination

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return (
            models.PostComment.objects
            .filter(post_id=post_id)
            .select_related('user')
            .order_by('-created_at')
        )


class PostCommentUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=serializers.PostCommentSerializer)
    def patch(self, request, comment_id):
        comment = get_object_or_404(models.PostComment, id=comment_id)

        if comment.user != request.user:
            return Response(
                {"status": False, "message": "You can't edit this comment."},
                status=403
            )

        serializer = serializers.PostCommentSerializer(
            comment,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Comment updated!", "data": serializer.data},
                status=200
            )

        return Response(serializer.errors, status=400)


class PostCommentDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(models.PostComment, id=comment_id)

        if comment.user != request.user:
            return Response(
                {"status": False, "message": "You can't delete this comment."},
                status=403
            )

        comment.delete()
        return Response(
            {"status": True, "message": "Comment deleted!"},
            status=200
        )
   
class PostLikeToggle(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(models.UserPost, id=post_id)
        user = request.user

        channel_layer = get_channel_layer()

        like, created = models.PostLike.objects.get_or_create(
            user=user,
            post=post
        )

        # 🔴 UNLIKE
        if not created:
            like.delete()
            return Response(
                {'status': True, 'message': 'Like removed!'},
                status=status.HTTP_200_OK
            )

        if post.user != user:

            Notification.objects.create(
                sender=user,
                receiver=post.user,
                post=post,
                notification_type="like"
            )

            # async_to_sync(channel_layer.group_send)(
            #     f"user_{post.user.id}",
            #     {
            #         "type": "send_notification",
            #         "data": {
            #             "type": "like",
            #             "message": f"{user.username} liked your post",
            #             "post_id": post.id
            #         }
            #     }
            # )

        return Response(
            {'status': True, 'message': 'Liked!'},
            status=status.HTTP_201_CREATED
        )


class UserDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        operation_description="""
        Retrieves detailed information about a specific user, including all their posts.
        """
    )
    def get(self, request, user_id):
        user = get_object_or_404(models.User, id=user_id)
        posts = (
            models.UserPost.objects
            .filter(user=user)
            .prefetch_related('medias', 'likes', 'tag')
        )

        serializer = serializers.UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostTagListCreateView(generics.ListCreateAPIView):
    queryset = models.PostTag.objects.all().order_by('title')
    serializer_class = serializers.PostTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination.DefaultPagination

    @swagger_auto_schema(
        operation_description="""
        GET: Lists all tags with search and pagination support.
        POST: Creates a new tag. Only authenticated users can create tags.
        """
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

class TagPostListView(generics.ListAPIView):
    """
    ✅ All posts related to a specific tag
    """
    serializer_class = serializers.UserPostDetailSerializer
    pagination_class = pagination.DefaultPagination

    @swagger_auto_schema(
        operation_description="""
        Retrieves all posts associated with a specific tag.
        Includes related tag, user, and media information.
        """
    )
    def get_queryset(self):
        tag_id = self.kwargs['tag_id']
        tag = get_object_or_404(models.PostTag, id=tag_id)
        return (
            models.UserPost.objects.filter(tag=tag, is_status=True)
            .select_related('tag', 'user')
            .prefetch_related('medias', 'likes')
            .order_by('-id')
        )