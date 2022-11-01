from datetime import date

from ._command import MyBaseCommand

from core.models import Term


class Command(MyBaseCommand):
	help = 'Update term information'

	def handle_school(self, scraper, options):

		scraper.update_terms()
		t = Term.set_school(scraper.school)

		today = date.today()
		year  = today.year
		month = today.month

		# Display terms
		# Last display term
		if month <= 5:
			c = f'{year-1}08'
		else:
			c = f'{year}01'
		t.filter(code_std__gte=c).update(display=True)
		t.filter(code_std__lt=c).update(display=False)

		# Last update term
		if month == 1:
			c = f'{year}01'
		elif 2 <= month <= 5:
			c = f'{year}05'
		elif 6 <= month <= 8:
			c = f'{year}08'
		else:
			c = f'{year+1}01'
		t.filter(code_std__gte=c).update(update=True)
		t.filter(code_std__lt=c).update(update=False)

		# Default term
		if month <= 2:
			c = f'{year}01'
		elif 3 <= month <= 9:
			c = f'{year}08'
		else:
			c = f'{year+1}01'

		# first() returns None if no matching objects
		term = (
			t.filter(code_std=c).first() or
			t.filter(display=True).exclude(code_std__endswith='05')[0]
		)
		term.default = True
		term.save()

		t.exclude(id=term.id).update(default=False)

		if options['verbosity'] >= 1:
			self.log(f"[info] Using term {term} as default")
