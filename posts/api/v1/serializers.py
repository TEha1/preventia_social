from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers
from posts.models import Post, Like, Comment, Attachment
from users.api.v1.serializers import UserDetailsSerializer


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            'id',
            'post',
            'file',
        ]


class PostSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    post_attachments = AttachmentSerializer('post_attachments', many=True, fields=['id', 'file', ], read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'text',
            'is_draft',
            'time_since',
            'is_liked',
            'likes_count',
            'comments_count',
            'post_attachments',
        ]
        extra_kwargs = {
            'user': {'read_only': True, },
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super(PostSerializer, self).create(validated_data)

    def to_representation(self, post):
        data = super(PostSerializer, self).to_representation(post)
        data['user'] = UserDetailsSerializer(
            post.user,
            context=self.context
        ).data
        return data

    def get_is_liked(self, post):
        request = self.context.get('request')
        if request:
            return Like.objects.filter(post=post, user=request.user).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'post',
            'text',
            'time_since',
        ]
        extra_kwargs = {
            'user': {'read_only': True, },
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super(CommentSerializer, self).create(validated_data)

    def to_representation(self, comment):
        data = super(CommentSerializer, self).to_representation(comment)
        data['user'] = UserDetailsSerializer(
            comment.user,
            context=self.context
        ).data
        return data
