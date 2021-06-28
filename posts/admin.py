from django.contrib import admin

from posts.models import Post, Attachment, Comment, Like
from utilities.admin import BaseAdmin


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = [
        'user',
        'text',
        'is_draft',
        'created_at',
        'modified_at',
        'manage_buttons',
    ]


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = [
        'user',
        'post',
        'text',
        'created_at',
        'modified_at',
        'manage_buttons',
    ]
    search_fields = [
        'user__username',
        'post__text',
    ]


@admin.register(Like)
class LikeAdmin(BaseAdmin):
    list_display = [
        'user',
        'post',
        'created_at',
        'modified_at',
        'manage_buttons',
    ]
    search_fields = [
        'user__username',
        'post__text',
    ]


@admin.register(Attachment)
class AttachmentAdmin(BaseAdmin):
    list_display = [
        'post',
        'file',
        'created_at',
        'modified_at',
        'manage_buttons',
    ]
    search_fields = [
        'post__text',
    ]
