from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, pre_save

from axes.signals import user_locked_out
from axes.utils import reset
from axes.models import AccessAttempt

from rest_framework import status
from rest_framework.exceptions import Throttled

User = get_user_model()


@receiver(user_locked_out)
def handle_user_locked_out(sender, request, username, **kwargs):
    user = User.objects.filter(username=username).first()
    if not user:
        return
    elif user and user.is_superuser:
        reset(username=username)
        raise CustomThrottledException(detail="Неверное имя пользователя и/или пароль")
    else:
        user.is_active = False
        user.save()
        raise Throttled(
            detail="Ваш аккаунт заблокирован. Для разблокировки учетной записи обратитесь к системному администратору"
        )


@receiver(post_delete, sender=AccessAttempt)
def handle_access_attempt_deleted(sender, instance, **kwargs):
    user = User.objects.filter(username=instance.username).first()
    if user and not AccessAttempt.objects.filter(username=instance.username).exists():
        user.is_active = True
        user.save()


@receiver(pre_save, sender=User)
def handle_user_check_is_active(sender, instance, **kwargs):
    if instance.is_active:
        AccessAttempt.objects.filter(username=instance.username).delete()


@receiver(post_save, sender=User)
def reset_failed_login_attempts(sender, instance, created, **kwargs):
    if created:
        failed_logins = AccessAttempt.objects.filter(username=instance.username)
        failed_logins.delete()


class CustomThrottledException(Throttled):
    status_code = status.HTTP_401_UNAUTHORIZED
    available_in = None
