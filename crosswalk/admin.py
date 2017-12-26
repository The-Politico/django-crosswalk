from crosswalk.models import ApiUser
from django.contrib import admin


class ApiUserAdmin(admin.ModelAdmin):
    fields = ('user',)
    list_display = ('user', 'token',)


admin.site.register(ApiUser, ApiUserAdmin)
