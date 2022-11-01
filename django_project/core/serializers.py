from rest_framework.serializers import ModelSerializer, ReadOnlyField

from .models import School, Professor, Term, Subject, Course, Section


class SchoolSerializer(ModelSerializer):
	class Meta:
		model = School
		fields = ('name', 'short_name', 'color_hex')


class ProfessorSerializer(ModelSerializer):
	class Meta:
		model = Professor
		fields = ('email', 'firstname', 'lastname')


class TermSerializer(ModelSerializer):
	class Meta:
		model = Term
		fields = ('code', 'description')


class SubjectSerializer(ModelSerializer):
	class Meta:
		model = Subject
		fields = ('short_title', 'long_title')


class CourseSerializer(ModelSerializer):
	subject__short_title = ReadOnlyField(source='subject.short_title')

	class Meta:
		model = Course
		fields = (
			'subject__short_title', 'number', 'title', 'credit_hours'
		)


class SectionSerializer(ModelSerializer):
	course__subject__short_title = ReadOnlyField(source='course.subject.short_title')
	course__number = ReadOnlyField(source='course.number')
	course__title = ReadOnlyField(source='course.title')
	term__code = ReadOnlyField(source='term.code')
	professor__firstname = ReadOnlyField(source='professor.firstname')
	professor__lastname = ReadOnlyField(source='professor.lastname')

	class Meta:
		model = Section
		fields = (
			'course__subject__short_title',
			'course__number', 'course__title',
			'term__code', 'crn', 'section_num', 'section_title', 'credit_hours',
			'professor__firstname', 'professor__lastname',
			'days', 'start_time', 'end_time', 'room',
			'enrolled', 'capacity'
		)
