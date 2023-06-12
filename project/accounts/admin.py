from axes.models import AccessAttempt

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import StudyField, User


class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "middle_name",
        "is_blocked",
        "date_added",
        "last_update",
    )
    list_filter = ("is_superuser", "is_metodist", "is_teacher")
    actions = ["unblock_users"]

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
    search_fields = ("username", )

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
admin.site.register(StudyField)
