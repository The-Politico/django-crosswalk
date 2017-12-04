from crosswalk.models import ApiUser
from django.contrib import admin


class ApiUserAdmin(admin.ModelAdmin):
    readonly_fields = ('token',)
    fields = ('user', 'token',)


admin.site.register(ApiUser, ApiUserAdmin)
