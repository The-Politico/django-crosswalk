from django.contrib import admin

from crosswalk.models import ApiUser


class ApiUserAdmin(admin.ModelAdmin):
    fields = ("user", "token")
    readonly_fields = ("token",)
    list_display = ("user", "token")


admin.site.register(ApiUser, ApiUserAdmin)
