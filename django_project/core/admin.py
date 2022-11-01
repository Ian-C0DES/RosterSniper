from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.functions import Substr

from .models import *

# TODO: Order apps better

# https://github.com/django/django/blob/master/django/contrib/admin/sites.py
admin.site.site_title = 'RS Admin'
admin.site.site_header = 'RosterSniper Admin'
admin.site.index_title = 'Welcome to the RosterSniper admin page!'
admin.site.enable_nav_sidebar = False


@admin.register(WebScraper)
class WebScraperAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	list_display = ('__str__',)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
	search_fields = ('name', 'short_name')
	list_filter = ('active', 'web_scraper',)
	list_display = ('__str__', 'short_name', 'web_scraper', 'active')

	change_form_template = "admin/school_change_form.html"

	actions = ['activate_schools', 'deactivate_schools']

	def activate_schools(self, request, queryset):
		queryset.update(active=True)
		self.message_user(
			request,
			'Selected schools were marked as active.',
			messages.SUCCESS
		)
	activate_schools.short_description = 'Activate selected schools'

	def deactivate_schools(self, request, queryset):
		queryset.update(active=False)
		self.message_user(
			request,
			'Selected schools were marked as inactive.',
			messages.SUCCESS
		)
	deactivate_schools.short_description = 'Deactivate selected schools'


@admin.register(SuggestedSchool)
class SuggestedSchoolAdmin(admin.ModelAdmin):
	search_fields = ('school_name',)
	list_display = ('school_name', 'edu_site', 'submitted')

	# Fields with auto_now_add=True aren't editable and therefore aren't
	# displayed in the admin by default
	# https://stackoverflow.com/a/23660030
	readonly_fields = ('submitted',)


class YearFilter(admin.SimpleListFilter):

	title = parameter_name = 'year'

	def lookups(self, request, model_admin):
		return [
			(x, x)
			for x in Term.objects.annotate(year=Substr('code', 1, 4))
				.order_by('-year').distinct().values_list('year', flat=True)
		]

	def queryset(self, request, queryset):
		return queryset.filter(code__startswith=x) if (x := self.value()) else queryset


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
	search_fields = ('code', 'description')
	list_filter = ('school', 'display', 'update', YearFilter)
	list_display = ('__str__', 'code', 'display', 'default', 'update')


class MyInline(admin.TabularInline):
	show_change_link = True
	extra = 0

	def has_add_permission(self, request, obj):
		return False


class SectionInline(MyInline):
	model = Section

	fields = ('__str__',)
	readonly_fields = ('__str__',)


class CourseInline(MyInline):
	model = Course

	readonly_fields = ('number', 'title')


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
	search_fields = ('firstname', 'lastname', 'email')
	list_display = ('__str__', 'email', 'section_count')

	inlines = [SectionInline]

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		queryset = queryset.annotate(Count("section"))
		return queryset.order_by(*Professor._meta.ordering)

	def section_count(self, obj):
		return obj.section__count
	section_count.admin_order_field = 'section__count'
	section_count.short_description = 'Number of Sections'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	search_fields = ('short_title__exact', 'long_title')
	list_display = ('short_title', 'long_title', 'course_count')
	inlines = [CourseInline]

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		queryset = queryset.annotate(Count("course"))
		return queryset

	def course_count(self, obj):
		return obj.course__count
	course_count.admin_order_field = 'course__count'
	course_count.short_description = 'Number of Courses'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	search_fields = ('subject__pk__iexact', 'number__exact', 'title')
	list_display = ('__str__', 'section_count')
	list_filter = ('subject',)
	inlines = [SectionInline]

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		queryset = queryset.annotate(Count("section"))
		return queryset.order_by(*Course._meta.ordering)

	def section_count(self, obj):
		return obj.section__count
	section_count.short_description = 'Number of Sections'
	section_count.admin_order_field = 'section__count'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
	search_fields = [
		'course__subject__pk__iexact',
		'course__number__exact', 'course__title',
		'crn__exact', 'section_num__exact',
		'professor__firstname', 'professor__lastname'
	]
	list_display = ('__str__', 'enrolled', 'capacity')
	list_filter = ('term', 'course__subject')
	list_select_related = ('course',)
	autocomplete_fields = ('professor',)

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		return queryset.order_by(*Section._meta.ordering)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
	search_fields = ('user__email', 'section__section_title')
	list_display = ('user', 'get_section', 'email_notify')
	list_filter = ('email_notify', 'section__term')

	def get_section(self, obj):
		return obj.section.get_code()
	get_section.short_description = 'Section'
	get_section.admin_order_field = 'section'

	readonly_fields = ('user', 'section')
