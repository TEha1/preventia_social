from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from preventia_social.settings import AUTH_USER_MODEL
from utilities.models import BaseModel


class User(AbstractUser):
    NORMAL = 1
    ADMIN = 2

    ROLE_CHOICES = (
        (NORMAL, "normal"),
        (ADMIN, "admin"),
    )

    username = models.CharField(
        max_length=100,
        unique=True,
        error_messages={
            'unique': _("This user already registered."),
        },
        verbose_name=_('username'),
    )
    email = models.EmailField(
        blank=True,
        null=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
        verbose_name=_('email address')
    )
    personal_image = models.ImageField(
        upload_to='user-images/',
        blank=True,
        null=True,
        verbose_name=_("personal image")
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES,
        default=NORMAL,
        verbose_name=_("role")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at")
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("modified at")
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", ]

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.is_superuser or self.is_staff:
                self.role = self.ADMIN
        return super(User, self).save()


class FriendShip(BaseModel):
    WAITING = "waiting"
    ACCEPTED = "accepted"

    STATUS_CHOICES = [
        (WAITING, _("waiting")),
        (ACCEPTED, _("accepted")),
    ]

    sender = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sender_friend_ships',
        verbose_name=_("user"),
    )
    receiver = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name='receiver_friend_ships',
        verbose_name=_("receiver")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=WAITING,
        verbose_name=_("status")
    )

    class Meta:
        verbose_name = _("friend ship")
        verbose_name_plural = _("friend ships")
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_friend_request'),
        ]

    def __str__(self):
        return f'{self.get_status_display()}'

    def accept(self):
        self.status = self.ACCEPTED
        self.save()

