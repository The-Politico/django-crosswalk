from django.contrib import admin

from crosswalk.models import ApiUser


class ApiUserAdmin(admin.ModelAdmin):
    readonly_fields = ('token',)
    fields = ('user', 'token',)


admin.site.register(ApiUser, ApiUserAdmin)
