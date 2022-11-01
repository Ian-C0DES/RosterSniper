from ._command import MyBaseCommand

from core.models import Term


class Command(MyBaseCommand):
	help = 'Update section information'

	def add_arguments(self, parser):

		super().add_arguments(parser)

		parser.add_argument(
			'-t', '--terms',
			type=int, nargs='*',
			help='Terms that the program will fetch section information from (eg: 202005). Defaults to all Term model instances with update=True.'
		)

		parser.add_argument(
			'--term-mode',
			type=int, choices=[0, 1, 2], default=2,
			help='Used when updating sections to determines which terms to use. 2: update=True (default), 1: display=True, 0: all.'
		)

		parser.add_argument('-i', '--infile', action='store_true',
			help='Update the database using the specified JSON file')

		parser.add_argument('-o', '--outfile', action='store_true',
			help='Output the course information to the specified file in JSON format')

	def handle_school(self, scraper, options):

		t = Term.set_school(scraper.school)

		# First update subject and course info using most recent term
		term = t.first()

		# self.log(f'[info] Updating subjects and courses using latest term: {term}')
		scraper.update_subjects(term)
		scraper.update_courses(term)

		if x := options['terms']:
			terms = t.filter(code__in=x)
		elif m := options['term_mode']:
			if m == 2:
				terms = t.filter(update=True)
			elif m == 1:
				terms = t.filter(display=True)
			elif m == 0:
				terms = t
		else:
			return

		for term in terms:
			# self.log(f'[info] Updating sections for {term}')
			scraper.update_sections(term)
