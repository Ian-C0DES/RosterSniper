from django.http import JsonResponse, Http404
from django.shortcuts import render

from ..models import School, Professor, Term, Subject, Course, Section


def api_about(request):
	return render(request, 'api_about.html')


def schools(request):
	s = School.objects.filter(active=True).values(
		'name', 'short_name', 'color_hex'
	)
	return JsonResponse(list(s), safe=False)


def view_maker(queryset):

	def view(request, school):
		try:
			s = School.objects.get(short_name=school)
		except School.DoesNotExist:
			raise Http404()

		# Closure
		qs = queryset.filter(school=s)

		try:
			if offset := request.GET.get('offset'):
				if (offset := int(offset)) >= 0:
					qs = qs[offset:]
				else:
					return JsonResponse('offset must be non-negative', safe=False)

			if limit := request.GET.get('limit'):
				if (limit := int(limit)) >= 0:
					qs = qs[:limit]
				else:
					return JsonResponse('limit must be non-negative', safe=False)

		except ValueError:
			return JsonResponse('offset/limit must be non-negative integers', safe=False)

		return JsonResponse(list(qs), safe=False)

	return view


professors = view_maker(
	Professor.objects.values(
		'email', 'firstname', 'lastname'
	)
)

terms = view_maker(
	Term.objects.filter(display=True).values(
		'code', 'description'
	)
)

subjects = view_maker(
	Subject.objects.values(
		'short_title', 'long_title'
	)
)

courses = view_maker(
	Course.objects.values(
		'subject__short_title', 'number', 'title', 'credit_hours'
	)
)

sections = view_maker(
	Section.objects.values(
		'course__subject__short_title',
		'course__number', 'course__title',
		'term__code', 'crn', 'section_num', 'section_title', 'credit_hours',
		'professor__firstname', 'professor__lastname',
		'days', 'start_time', 'end_time', 'room',
		'enrolled', 'capacity'
	)
)
