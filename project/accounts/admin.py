from axes.models import AccessAttempt

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import StudyField, User


class CustomUserAdmin(BaseUserAdmin):
    readonly_fields = ("is_teacher",)
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "middle_name",
        "is_blocked",
        "is_active",
        "access_attempts",
        "date_added",
        "last_update",
    )
    list_filter = ("is_superuser", "is_metodist", "is_teacher", "is_active")
    actions = ["unblock_users", "block_users"]

    fieldsets = ()
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "study_fields",
                    "is_superuser",
                    "is_metodist",
                    "is_teacher",
                ),
            },
        ),
    )
    filter_horizontal = ("study_fields",)
    search_fields = ("username",)

    def access_attempts(self, obj):
        attempt = AccessAttempt.objects.filter(username=obj.username).first()
        if not attempt:
            return 0
        return attempt.failures_since_start

    access_attempts.short_description = "failured attempts"

    def is_blocked(self, obj):
        if obj.is_active:
            return "Активный"
        return "Заблокирован"

    is_blocked.short_description = "Статус"

    def unblock_users(self, request, queryset):
        for user in queryset:
            user.is_active = True
            user.save()

    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    unblock_users.short_description = "Разблокировать"
    block_users.short_description = "Заблокировать"


admin.site.register(User, CustomUserAdmin)
admin.site.register(StudyField)
