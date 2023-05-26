from django.dispatch import receiver
from axes.signals import user_locked_out
from rest_framework.exceptions import Throttled
from django.contrib.auth import get_user_model
from axes.utils import reset
from rest_framework import status

User = get_user_model()


@receiver(user_locked_out)
def handle_user_locked_out(sender, request, username, **kwargs):
    user = User.objects.filter(username=username).first()
    if user and user.is_superuser:
        reset(username=username)
        raise CustomThrottledException(
            detail={"non_field_errors": ["Неверное имя пользователя и/или пароль."]}, code="throttled"
        )
    else:
        raise Throttled(
            detail="Ваш аккаунт заблокирован. Для разблокировки учетной записи обратитесь к системному администратору."
        )


class CustomThrottledException(Throttled):
    status_code = status.HTTP_400_BAD_REQUEST
    available_in = None
