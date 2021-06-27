from django.urls import path, include
from rest_framework.routers import DefaultRouter

from posts.api.v1.views import PostResource, CommentResource, AttachmentResource

app_name = "posts"

router = DefaultRouter()

router.register(r'posts', PostResource, basename='posts')
router.register(r'attachments', AttachmentResource, basename='attachments')
router.register(r'comments', CommentResource, basename='comments')

urlpatterns = (
    path("", include(router.urls)),
)
