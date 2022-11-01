from ._command import MyBaseCommand

from core.models import Section


class Command(MyBaseCommand):
	help = "Update seat information for favorited sections"

	def handle_school(self, scraper, options):

		"""
		We're not iterating over all the favorites since multiple users can
		watch the same section, and we don't want to make a request twice or
		keep track of already updated sections.

		The update_section_seats(s) method should call s.set_enrollment(...)
		which automatically emails all of the appropriate users.

		The .order_by() clears the Section's default sort which gets rid of
		an INNER JOIN and ORDER BY in the query.
		"""
		sections = Section.objects.filter(
			school=scraper.school,
			term__update=True,
			favorite__user__email_confirmed=True,
			favorite__user__email_notify=True,
			favorite__email_notify=True
		).order_by().distinct()
		verbosity = options["verbosity"]

		for s in sections:
			scraper.update_section_seats(s)
			if verbosity > 1:
				self.log(f"[{s.get_log_str()}] Seats: {s.get_enrollment()}")

		self.log(f"[info] Updated {len(sections)} favorites")
