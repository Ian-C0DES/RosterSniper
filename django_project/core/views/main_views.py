from functools import reduce
import datetime
import operator
import re

from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from core.models import School, Term, Section, Favorite


# Helper function, not a view
def get_school(school):
	try:
		return School.objects.get(active=True, short_name=school)
	except School.DoesNotExist:
		raise Http404()


def get_courses(request, school):

	s = get_school(school)

	if term := request.GET.get('term'):
		# The custom order_by is needed so the regroups work in the template
		sections = (
			Section.objects
			.order_by('course', 'section_title', 'section_num')
			.select_related('professor', 'course', 'course__subject')
			.filter(school=s, term=term)
		)
	else:
		return JsonResponse(data={})

	query = Q()

	if q := request.GET.get('q'):
		#
		# TODO: split on : and - characters also
		# https://stackoverflow.com/a/23720594
		#
		for term in q.split():
			query &= (
				Q(crn__exact=term)
				| Q(section_num__exact=term)
				| (
					Q(section_title__contains=term)
					if term.isupper() else Q(section_title__icontains=term)
				)
				| Q(course__number__exact=term)
				| Q(course__subject__short_title__iexact=term)
			)

	if days := request.GET.get('days'):
		query &= Q(days__contains=days)

	if crsNumMin := request.GET.get('crsNumMin'):
		query &= Q(course__number__gte=crsNumMin)
	if crsNumMax := request.GET.get('crsNumMax'):
		query &= Q(course__number__lte=crsNumMax)

	if creditHourExact := request.GET.get('creditHourExact'):
		query &= Q(credit_hours=creditHourExact)
	if creditHourMin := request.GET.get('creditHourMin'):
		query &= Q(credit_hours__gte=creditHourMin)
	if creditHourMax := request.GET.get('creditHourMax'):
		query &= Q(credit_hours__lte=creditHourMax)

	if professor := request.GET.get('professor'):
		for term in professor.split():
			query &= Q(professor__firstname__icontains=term) \
				| Q(professor__lastname__icontains=term)

	if room := request.GET.get('room'):
		query &= Q(room__icontains=room.replace(' ', '-'))

	sections = sections.filter(query)

	return JsonResponse(
		data={
			'courses': render_to_string(
				'courses/add_courses_rows.html', {
					'all_sections': sections,
					'crns': request.user.section_set.values_list('crn', flat=True)
						if request.user.is_authenticated else None
				},
				request = request
			)
			# 'user': render_to_string( 'military_time': request.user.military_time;
		},
		safe=False
	)


def add_courses(request, school):
	""" The Add Courses page lets users search for and favorite sections. """

	s = get_school(school)

	return render(
		request,
		'courses/add_courses.html',
		{
			'terms': Term.objects.filter(school=s, display=True)
				.values('id', 'default', 'description'),
			'school': s
		}
	)


def add_courses_(request):

	return render(
		request,
		'courses/add_courses_.html',
		{ 'schools': School.objects.filter(active=True) }
	)


def get_rooms(request, school):

	s = get_school(school)

	# Get all sections (with a room) for the given school
	if term := request.GET.get('term'):
		sections = (
			Section.objects
			.order_by('room')
			.filter(school=s, term__code=term)
			.exclude(room='')
		)
	else:
		return JsonResponse(data={})

	# get all room ids
	room_ids = set(sections.values_list('room', flat=True).distinct())

	# Find all classes taking place in the specified time window
	query = Q()

	# check the day
	if days := request.GET.get('days'):
		query &= reduce(operator.or_, (Q(days__contains=x) for x in days))

	# check start/end times
	time_start = datetime.time(0, 0)
	time_end = datetime.time(23, 59)

	if request_start := request.GET.get("timeStart"):
		times = re.findall(r'\d+', request_start)[:2]
		if len(times) == 2:
			times = [int(x) for x in times]
			if 'pm' in request_start.lower() and times[0] != 12:
				times[0] += 12
			time_start = datetime.time(*times)

	if request_end := request.GET.get("timeEnd"):
		times = re.findall(r'\d+', request_end)[:2]
		if len(times) == 2:
			times = [int(x) for x in times]
			if 'pm' in request_end.lower() and times[0] != 12:
				times[0] += 12
			time_end = datetime.time(*times)

	# A class does not intersect with a given time window if:
	# - The class ends before (lt) the window starts, or
	# - The class starts after (gt) the window ends
	# The following is the negation of that
	query &= Q(end_time__gte=time_start) & Q(start_time__lte=time_end)

	# run our query
	sections = sections.filter(query)

	# get only the room numbers
	unavailable_room_ids = set(sections.values_list('room', flat=True).distinct())

	# find all rooms that aren't in the list of rooms having classes at the given time
	available_room_ids = room_ids.difference(unavailable_room_ids)

	return JsonResponse(data={
		'startTime': time_start,
		'endTime': time_end,
		'days': days,
		'totalRoomCount': len(room_ids),
		'allRoomIDs': list(room_ids),
		'availableCount': len(available_room_ids),
		'unavailableCount': len(unavailable_room_ids),
		'availableRoomIDs': sorted(available_room_ids),
		'unavailableRoomIDs': list(unavailable_room_ids),
		'unavailableSections': list(sections.values())
	}, safe=False)


def find_rooms(request, school):

	s = get_school(school)

	return render(
		request,
		'rooms/room_finder.html',
		{
			'terms': Term.objects.filter(school=s, display=True),
			'school': s
		}
	)


def find_rooms_(request):

	return render(
		request,
		'rooms/room_finder_.html',
		{ 'schools': School.objects.filter(active=True) }
	)


@login_required
def my_courses(request):
	""" Shows user their favorites, lets them remove favorites, and lets them
	enable / disable email notifications. """

	if (
		request.method == 'GET'
		and (term := request.GET.get('term'))
		and (crn := request.GET.get('crn'))
	):

		if favorite := request.GET.get('favorite'):
			s = Section.objects.get(term_id=term, crn=crn)
			if favorite == 'true':
				request.user.section_set.add(s)
			elif favorite == 'false':
				request.user.section_set.remove(s)

		elif email := request.GET.get('email'):
			Favorite.objects.filter(
				user=request.user, section__term_id=term, section__crn=crn
			).update(email_notify=email == 'true')

		return HttpResponse('')

	else:
		return render(
			request,
			'courses/my_courses.html',
			{
				'favorites': request.user.favorite_set.all().select_related(
					'section', 'section__school',
					'section__term', 'section__professor',
					'section__course', 'section__course__subject'
				)
			}
		)
