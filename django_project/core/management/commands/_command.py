from importlib import import_module

from django.core.management.base import BaseCommand

from core.models import School


class MyBaseCommand(BaseCommand):

	def log(self, msg):
		self.stdout.write(msg)
		self.stdout.flush()

	def err(self, msg):
		self.stdout.write(self.style.ERROR(msg))
		self.stdout.flush()

	def add_arguments(self, parser):

		parser.add_argument(
			'-s', '--schools',
			nargs='*',
			help='WIP'
		)

	def handle(self, *args, **options):

		if s := options['schools']:
			schools = School.objects.filter(short_name__in=s)
		else:
			schools = School.objects.filter(active=True)

		for school in schools.select_related('web_scraper'):
			self.log(f'[info] School: {school}')
			scrapper = import_module(
				f'core.management.web_scrapers.{school.web_scraper.name}'
			).Scrapper(
				school,
				self.log,
				self.err,
				options
			)
			self.handle_school(scrapper, options)
			self.log('')

	def handle_school(self, scrapper, options):
		""" Override me pls """
		pass
