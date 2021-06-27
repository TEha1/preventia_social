from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from posts.api.v1.serializers import PostSerializer, CommentSerializer, AttachmentSerializer
from posts.models import Post, Comment, Attachment
from utilities.viewsets import (
    PostFilterClass, post_field_expand, comment_field_expand,
    attachment_field_expand
)


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=post_field_expand))
class PostResource(ModelViewSet):
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'user',
        'is_draft',
        'is_liked',
    ]
    filter_class = PostFilterClass
    search_fields = [
        'user__username',
        'text',
    ]
    ordering_fields = [
        'created_at',
        'text',
    ]

    def get_queryset(self):
        if self.action in ['update', 'partial_update', ]:
            queryset = Post.objects.filter(user_id=self.request.user.id, is_draft=False)
        else:
            queryset = Post.objects.filter(is_draft=False)
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post', ], url_path='like-dislike', url_name='like_dislike')
    def like_unlike(self, request, pk):
        post = self.get_object()
        sponsored = post.like_dislike(self.request.user.id)

        if sponsored:
            message = _("post liked")
        else:
            message = _("post disliked")

        return Response(
            {
                "details": message,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=comment_field_expand))
class CommentResource(ModelViewSet):
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'user',
        'post',
    ]
    search_fields = [
        'user__username',
        'text',
    ]
    ordering_fields = [
        'created_at',
        'text',
    ]

    def get_queryset(self):
        if self.action in ['update', 'partial_update', ]:
            queryset = Comment.objects.filter(user_id=self.request.user.id)
        else:
            queryset = Comment.objects.all()
        return queryset.order_by('-created_at')


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=attachment_field_expand))
class AttachmentResource(ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = AttachmentSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = [
        'post',
    ]

    def get_queryset(self):
        if self.action in ['create', 'destroy']:
            return Attachment.objects.filter(post__user_id=self.request.user.id)
        return Attachment.objects.all()
