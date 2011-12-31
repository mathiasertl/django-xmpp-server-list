from django.contrib import admin

from models import ConfirmationKey, UserProfile

admin.site.register(UserProfile)
admin.site.register(ConfirmationKey)