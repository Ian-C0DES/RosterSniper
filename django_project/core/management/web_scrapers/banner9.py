import json
import re

from datetime import time
from html import unescape

import requests

from core.models import Professor, Term, Subject, Course, Section


def season(description):
	if "spring" in description:
		return "01"
	elif "summer" in description:
		return "05"
	elif "fall" in description:
		return "08"

	return "00"


# Some Banner 9 documentation: https://jennydaman.gitlab.io/nubanned/dark
class Scrapper:

	def __init__(self, school, log, err, options):
		# E.g. https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/
		self.school = school
		self.url = school.url
		self.log = log
		self.err = err

		self.options = options
		self.verbosity = options["verbosity"]

	def _get_with_session(self, term, url, item=""):

		# Establish a session with the given term (saves cookies)
		session = requests.Session()
		session.get(self.url + f"term/search?mode=search&term={term.code}", timeout=5)

		x = []
		total = 1
		while len(x) < total:
			# First we replace all &quot; with single quotes because unescape
			# would replace them with double quotes which messes with the JSON.
			# After that, unescape covers the regular &amp; -> & and &#39; -> '
			r = json.loads(unescape(
				session.get(
					self.url + url.format(term=term.code, offset=len(x))
				).text.replace("&quot;", "'")
			))

			x.extend(r["data"])
			total = r["totalCount"]

			if self.verbosity >= 1:
				self.log(f"[{term}] Downloaded {len(x)}/{total} {item}")

		return x

	def update_terms(self):

		# Get a list of the 50 most recent terms. The response looks like
		# [{'code': '202105', 'description': 'Summer 2021'}, ...]
		r = requests.get(self.url + "courseSearch/getTerms?offset=1&max=50", timeout=5).json()

		for json_term in r:

			d = json_term["description"].replace('Semester ', '').replace(' (View Only)', '')
			c = json_term["code"]

			if d[0] == "*" or len(d) >= 20:
				continue
			term, created = Term.objects.update_or_create(
				school=self.school,
				code=c,
				defaults={
					"code_std": c[:4] + season(d.lower()),
					"description": d
				}
			)

			if self.verbosity > 1:
				self.log(f"{'Created' if created else 'Updated'} term {term}")

		if self.verbosity >= 1:
			self.log(f"[info] Updated {len(r)} term(s)")

	def update_subjects(self, term):

		# Get all subjects for the given term. The response text looks like
		# [{"code": "ACCT", "description": "Accounting"}, ...]
		subjects = json.loads(unescape(
			requests.get(
				self.url + f"courseSearch/get_subject?term={term.code}&offset=1&max=500"
			).text
		))

		self.log(f"[{term}] Downloaded {len(subjects)} subject(s)")

		for subject in subjects:
			s, created = Subject.objects.update_or_create(
				school=self.school,
				short_title=subject["code"],
				defaults={"long_title": subject["description"]}
			)

			if self.verbosity > 1:
				self.log(f"[info] {'Created' if created else 'Updated'} {s.full_str}")

	def update_courses(self, term):

		courses = self._get_with_session(
			term,
			"courseSearchResults/courseSearchResults?txt_term={term}&pageOffset={offset}&pageMaxSize=500",
			"course(s)"
		)

		for course in courses:

			low  = course["creditHourLow"]
			high = course["creditHourHigh"]
			if high is None:
				credit_hours = str(low) if low is not None else ""
			else:
				credit_hours = f"{low}-{high}"

			c, created = Course.objects.update_or_create(
				school=self.school,
				subject=Subject.objects.get(
					school=self.school,
					short_title=course["subject"]
				),
				number=course["courseNumber"],
				defaults={
					"title": course["courseTitle"],
					"credit_hours": credit_hours
				}
			)

			if self.verbosity > 1:
				self.log(f"[info] {'Created' if created else 'Updated'} {c}")

	def update_sections(self, term):

		# Load section data from JSON file
		if self.options["infile"]:
			filename = f"data/{self.school.short_name}-{term.code}.json"
			sections = json.load(open(filename))

		else:
			sections = self._get_with_session(
				term,
				"searchResults/searchResults?txt_term={term}&pageOffset={offset}&pageMaxSize=500",
				"section(s)"
			)

		# Save section data if necessary
		if self.options["outfile"]:
			# Automatically create directory
			# https://stackoverflow.com/a/12517490
			filename = f"data/{self.school.short_name}-{term.code}.json"
			with open(filename, "w") as f:
				f.write(json.dumps(sections, indent="\t"))
				self.log(f"[info] Saved course information to {filename}")

		self.log(f"[{term}] Updating database")

		for s in sections:

			# We can't use update_or_create() here b/c it calls save() before mandatory fields are set
			crn = s["courseReferenceNumber"]
			try:
				section = Section.objects.get(
					school=self.school,
					term=term,
					crn=crn
				)
			except Section.DoesNotExist:
				section = Section(school=self.school, term=term, crn=crn)

			try:
				section.course = Course.objects.get(
					school=self.school,
					subject__short_title=s["subject"],
					number=s["courseNumber"]
				)
			except Course.DoesNotExist:
				self.log(f"[crn={crn}] New courses found, please run update courses")
				print(s)
				continue

			section.section_num = s["sequenceNumber"]

			# ' Digital Media', 'Digital Media.' etc.
			section.section_title = s["courseTitle"].strip(" .")

			if (credit_hours := s["creditHours"]) is None:
				section.credit_hours = s["creditHourLow"]
			else:
				section.credit_hours = credit_hours

			if faculty := s["faculty"]:
				professor = faculty[0]

				# Max split for
				# clemson: Lydia Lancaster Folger Schleifer
				# oakland: Mohammed (Professor Mahmoud) Mahmoud
				professor_name = professor["displayName"]
				if ", " in professor_name:
					professor_name = professor_name.split(", ", maxsplit=1)[::-1]
				else:
					professor_name = professor_name.split(" ", maxsplit=1)

				if len(professor_name) != 2:
					continue

				section.professor, _ = Professor.objects.update_or_create(
					school=self.school,
					email=professor["emailAddress"],
					defaults={
						"firstname": professor_name[0],
						"lastname": professor_name[1]
					}
				)

			else:
				section.professor = None

			# "meetingsFaculty" contains a list of all the different meetings.
			# For most courses there will only be one meeting, but lab courses will
			# usually have two. Some might not even have a 'meetingsFaculty'.
			days = room = ""
			if meetings := s.get("meetingsFaculty", []):
				meeting = meetings[0].get("meetingTime")

				if meeting.get("monday"):
					days += "M"
				if meeting.get("tuesday"):
					days += "T"
				if meeting.get("wednesday"):
					days += "W"
				if meeting.get("thursday"):
					days += "R"
				if meeting.get("friday"):
					days += "F"
				if meeting.get("saturday"):
					days += "S"
				if meeting.get("sunday"):
					days += "U"

				# This handles cases where the time isn't provided and cases where
				# the time is explicitly set to null (both default to "0000")
				start_time = meeting.get("beginTime", "0000") or "0000"
				start_time = time(int(start_time[:2]), int(start_time[2:]))

				end_time = meeting.get("endTime", "0000") or "0000"
				end_time = time(int(end_time[:2]), int(end_time[2:]))

				if (b := meeting["building"]) and (r := meeting["room"]):
					room = f"{b}-{r}"

			# If there were no scheduled meetings
			else:
				start_time = end_time = time(0, 0)

			section.days = days
			section.start_time = start_time
			section.end_time = end_time
			section.room = room

			section.set_enrollment(s["enrollment"], s["maximumEnrollment"])
			section.save()

			if self.verbosity > 1:
				self.log(f"[{term}] Updated {section}")

	def update_section_seats(self, section):
		""" Example response:

		<span class="status-bold">Enrollment Actual:</span> <span
				dir="ltr">42</span><br/>
		<span class="status-bold">Enrollment Maximum:</span> <span
				dir="ltr">40</span><br/>
		"""
		r = requests.post(
			self.url + f"searchResults/getEnrollmentInfo",
			data={"term": section.term.code, "courseReferenceNumber": section.crn},
		)

		# Regular expressions are a lot faster than BeautifulSoup,
		# and this regex is 4x faster than "\d+" (from my tests)
		matches = re.findall('dir="ltr">(.*?)</span>', r.text)

		if len(matches) == 2:
			# enrolled, capacity
			section.set_enrollment(int(matches[0]), int(matches[1]))
			section.save()

		else:
			# HTML might have changed
			self.log(
				f"[{section.get_log_str()}] Banner 9 class enrollment page might have changed:\n{r.text}"
			)
