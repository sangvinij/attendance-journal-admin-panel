from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User

from axes.models import AccessAttempt


class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("id", "first_name", "last_name", "username", "is_blocked")
    list_filter = ("username", "first_name", "last_name")
    actions = ["unblock_users"]

    fieldsets = ()
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password"),
            },
        ),
    )
    filter_horizontal = ()

    def is_blocked(self, obj):
        attempt = AccessAttempt.objects.filter(username=obj.username).first()
        if attempt and attempt.failures_since_start >= 3:
            return "Заблокирован"
        return "Активный"

    is_blocked.short_description = "Статус"

    def unblock_users(self, request, queryset):
        for user in queryset:
            AccessAttempt.objects.filter(username=user.username).delete()

    unblock_users.short_description = "Разблокировать"


admin.site.register(User, CustomUserAdmin)
