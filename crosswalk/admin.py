from crosswalk.models import ApiUser, Domain, Entity
from django.contrib import admin


class ApiUserAdmin(admin.ModelAdmin):
    readonly_fields = ('token',)
    fields = ('user', 'token',)


admin.site.register(ApiUser, ApiUserAdmin)
admin.site.register(Domain)
admin.site.register(Entity)
