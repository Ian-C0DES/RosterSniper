from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class MyUserCreationForm(UserCreationForm):

	class Meta:
		model = User
		fields = ['email', 'first_name', 'password1', 'password2', 'phone']

		help_texts = {
			'first_name': 'This field is optional and only used to personalize emails.',
			'phone': 'This field is optional and only used send updates on followed courses.'
		}


class UserUpdateForm(forms.ModelForm):

	class Meta:
		model = User
		fields = ['email', 'first_name', 'email_notify', 'phone', 'phone_notify', 'military_time']

		labels = {
			'email_notify': 'Receive emails',
			'phone': 'Phone number',
			'phone_notify': 'Receive SMS',
			'military_time': 'Military time'
		}
		help_texts = {
			'first_name': 'This field is optional and only used to personalize emails.',
			'email_notify': 'This enables/disables all emails from this site. To disable email notifications for individual sections use the envelope buttons on the My Courses page.',
			'phone_notify': 'This enables/disables all sms notifications from this site.',
			'military_time': 'This enables/disables 24-hour format across the site.'
		}
