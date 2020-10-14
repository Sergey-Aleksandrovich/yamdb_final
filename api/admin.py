from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

""" class ProfileAdmin(admin.ModelAdmin):
    list_display = ("bio", "role")
    search_fields = ("role",)
    list_filter = ("bio",)
    empty_value_display = '-пусто-'
 """


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)

# admin.site.register(Profile, ProfileAdmin)
