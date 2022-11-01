from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
	"""
	Custom Admin for custom User model. The differences are:
	- replaced username with email
	- added 'Notifications' fieldset
	- removed is_staff from list_display and list_filter
	(we don't really have non superuser staff, so its not important)
	- added email_confirmed to list_filter
	- removed last_name from search_fields because we don't use them
	"""

	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Personal info'), {'fields': ('first_name', 'last_name', 'military_time', 'phone')}),
		(_('Notifications'), {'fields': ('email_confirmed', 'email_notify', 'phone_notify')}),
		(_('Permissions'),
			{'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2'),
		}),
	)

	list_display = ('email', 'first_name', 'date_joined', 'last_login', 'email_confirmed')
	list_filter = ('email_confirmed', 'is_superuser', 'is_active', 'groups')
	search_fields = ('email', 'first_name')
	ordering = ('email',)
