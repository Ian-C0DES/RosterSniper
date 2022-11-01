from django.http import Http404

from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (
	SchoolSerializer, ProfessorSerializer, TermSerializer,
	SubjectSerializer, CourseSerializer, SectionSerializer
)
from .models import School, Term

class MyView(ListAPIView):
	http_method_names = ['get']

	# https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py
	pagination_class = LimitOffsetPagination


class Schools(MyView):
	queryset = School.objects.filter(active=True)
	serializer_class = SchoolSerializer


class PerSchool(MyView):

	def get_queryset(self):
		try:
			s = School.objects.get(short_name=self.kwargs['school'])
		except School.DoesNotExist:
			raise Http404()

		qs = self.qs if hasattr(self, 'qs') \
			else self.serializer_class.Meta.model.objects.all()

		return qs.filter(school=s)


class Professors(PerSchool):
	serializer_class = ProfessorSerializer


class Terms(PerSchool):
	serializer_class = TermSerializer
	qs = Term.objects.filter(display=True)


class Subjects(PerSchool):
	serializer_class = SubjectSerializer


class Courses(PerSchool):
	serializer_class = CourseSerializer


class Sections(PerSchool):
	serializer_class = SectionSerializer
