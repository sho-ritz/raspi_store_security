from django.contrib import admin
from .models import PurchaseLog, User, Item

admin.site.register(PurchaseLog)
admin.site.register(User)
admin.site.register(Item)