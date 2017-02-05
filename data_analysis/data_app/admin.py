from django.contrib import admin
from .models import Account, Year, Month, Transaction

admin.site.register(Account)
admin.site.register(Year)
admin.site.register(Month)
admin.site.register(Transaction)
