from django.contrib import admin
from .models import Account, Destination

class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ('account_id', 'account_name', 'email')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('account_id', 'account_name', 'email')

class DestinationAdmin(admin.ModelAdmin):
    model = Destination
    list_display = ('get_account_id', 'url', 'http_method')
    list_filter = ('is_deleted', 'created_at', 'http_method')
    search_fields = ('url', )

    def get_account_id(self, obj):
        return obj.account.account_id

    get_account_id.short_description = 'Account ID'

admin.site.register(Account, AccountAdmin)
admin.site.register(Destination, DestinationAdmin)
