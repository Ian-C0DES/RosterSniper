from django.urls import path, include
from core.views import main_views, api_views, other_views


urlpatterns = [
	path('', other_views.home, name='home'),
	path('about/', other_views.about, name='about'),

	path('<str:school>/', include([
		path('get-courses/', main_views.get_courses, name='get_courses'),
		path('add-courses/', main_views.add_courses, name='add_courses'),

		path('get-rooms/', main_views.get_rooms, name='get_rooms'),
		path('find-rooms/', main_views.find_rooms, name='find_rooms'),
	])),

	path('add-courses/', main_views.add_courses_, name='add_courses_'),
	path('find-rooms/', main_views.find_rooms_, name='find_rooms_'),

	path('add-school/', other_views.add_school, name='add-school'),

	path('my-courses/', main_views.my_courses, name='my_courses'),
	path('unsubscribe/<str:unsub_type>/<uuid:unsub_id>/', other_views.unsubscribe, name='unsubscribe'),

	# My API
	path('api/', api_views.api_about, name='api_about'),
	path('api/schools/', api_views.schools),
	path('api/<str:school>/', include([
		path('professors/', api_views.professors),
		path('terms/', api_views.terms),
		path('subjects/', api_views.subjects),
		path('courses/', api_views.courses),
		path('sections/', api_views.sections),
	])),

	# DRF
	# path('drf/schools/', drf_views.Schools.as_view()),
	# path('drf/<str:school>/', include([
	# 	path('professors/', drf_views.Professors.as_view()),
	# 	path('terms/', drf_views.Terms.as_view()),
	# 	path('subjects/', drf_views.Subjects.as_view()),
	# 	path('courses/', drf_views.Courses.as_view()),
	# 	path('sections/', drf_views.Sections.as_view()),
	# ]))
]
