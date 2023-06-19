from django.contrib.auth.backends import ModelBackend

from rest_framework.exceptions import Throttled


class CustomModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        active = getattr(user, "is_active", True)
        if not active:
            raise Throttled(
                detail="Ваш аккаунт заблокирован. Для разблокировки учетной записи "
                "обратитесь к системному администратору"
            )
        return active
