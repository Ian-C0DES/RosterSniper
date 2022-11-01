import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


"""
Based on
https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
https://tech.serhatteker.com/post/2020-01/email-as-username-django/
https://docs.djangoproject.com/en/stable/topics/auth/customizing/#a-full-example

Django's default UserManager:
https://github.com/django/django/blob/master/django/contrib/auth/models.py
"""
class UserManager(BaseUserManager):
	""" Custom user model manager where email is the unique identifier
	for authentication instead of username. """

	use_in_migrations = True

	def create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError('Users must have an email address')

		user = self.model(email=self.normalize_email(email), **extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
	username = None

	email = models.EmailField(unique=True)
	email_confirmed = models.BooleanField(default=False,
		help_text='Whether the user has clicked an activation link')

	email_notify = models.BooleanField(default=True,
		help_text='Whether the user should receive emails')
	email_unsub_id = models.UUIDField(default=uuid.uuid4)
	phone = models.CharField(max_length=15, blank=True, default='')
	phone_notify = models.BooleanField(default=False,
		help_text='Whether the user should receive SMS')
	military_time = models.BooleanField(default=False, help_text='Whether the user prefers military time')
	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def __str__(self):
		return self.email
