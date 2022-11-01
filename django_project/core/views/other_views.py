from random import randint

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from core.forms import SuggestedSchoolForm
from core.models import School, Favorite
from users.models import User


def home(request):
	return render(
		request,
		'home.html',
		{
			'schools': School.objects.filter(active=True).values('short_name', 'name')
		}
	)


def about(request):

	if request.method == 'POST':
		form = SuggestedSchoolForm(request.POST)
		if form.is_valid():
			form.save()
			messages.info(request, 'Thank you for your submission.')
			return redirect('about')

	else:
		form = SuggestedSchoolForm()

	names = ('Ryan Cosentino', 'Shaun Mitchell')
	temp = randint(0, 1)
	context = {
		'name1': names[temp],
		'name2': names[1 - temp],
		'form': form
	}

	return render(request, 'about.html', context)


def unsubscribe(request, unsub_type, unsub_id):
	"""
	Unsubscribe requests contain an unsub_type and an unsub_id. The unsub_id is
	used to safely allow users to unsubscribe without logging in by clicking a
	link sent within an email, accessing a URL unique to the particular
	unsubscribe request. Because there are 2^122 different version 4 UUIDs it is
	unlikely that someone would guess a correct one or even want to.
	"""

	try:
		if unsub_type == 'favorite':
			unsub_object = Favorite.objects.get(email_unsub_id=unsub_id)
			text = f'emails related to {unsub_object.section}'

		elif unsub_type == 'all':
			unsub_object = User.objects.get(email_unsub_id=unsub_id)
			text = 'all emails'

		else:
			raise ObjectDoesNotExist()

		# Ordinarily unsubscribe links sent in emails will not have the
		# 'subscribe' parameter in the query string so the following will
		# evaluate to False.
		#
		# This is meant to be used by a button on the unsubscribe page that lets
		# users re subscribe by making a GET request in the background. It
		# doesn't actually matter what the argument is, as long as it exists.
		unsub_object.email_notify = request.GET.get('subscribe') is not None
		unsub_object.save()

		return render(request, 'unsubscribe.html', {'text': text})

	except ObjectDoesNotExist:
		return render(
			request,
			'base/message.html',
			{
				'title': 'Unsubscribe Error',
				'message': 'Your unsubscribe link is invalid! 😕'
			}
		)

def add_school(request):
	return render(request,"add_school.html")
