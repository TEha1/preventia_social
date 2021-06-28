from django.db import models
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from preventia_social.settings import AUTH_USER_MODEL
from utilities.models import BaseModel


class Post(BaseModel):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="user_posts",
        verbose_name=_("user")
    )
    text = models.TextField(
        verbose_name=_("post content")
    )
    is_draft = models.BooleanField(
        default=False,
        verbose_name=_("is draft")
    )

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ['-id']
        indexes = [
            models.Index(fields=['text', ]),
        ]

    def __str__(self):
        return f'post - {self.pk}'

    @property
    def time_since(self):
        return timesince(self.created_at)

    @property
    def likes_count(self):
        return self.favorite_posts.count()

    @property
    def comments_count(self):
        return self.post_comments.count()

    def like_dislike(self, user_id):
        likes = Like.objects.filter(post=self, user_id=user_id)
        if likes.exists():
            likes.delete()
            return False
        else:
            Like.objects.create(post=self, user_id=user_id)
            return True


class Attachment(BaseModel):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="post_attachments",
        verbose_name=_("post")
    )
    file = models.FileField(
        verbose_name=_("file")
    )

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self):
        return f'{self.post}'


class Comment(BaseModel):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user")
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="post_comments",
        verbose_name=_("post")
    )
    text = models.TextField(
        verbose_name=_("comment text")
    )

    class Meta:
        verbose_name = _("post comment")
        verbose_name_plural = _("post comments")

    def __str__(self):
        return f'{self.text}'

    @property
    def time_since(self):
        return timesince(self.created_at)


class Like(BaseModel):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="favorite_posts",
        verbose_name=_("post")
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_likes",
        verbose_name=_("user")
    )

    class Meta:
        verbose_name = _("post like")
        verbose_name_plural = _("post likes")
        ordering = ['-id', ]
        unique_together = ('user', 'post',)

    def __str__(self):
        return f'{self.post}'
