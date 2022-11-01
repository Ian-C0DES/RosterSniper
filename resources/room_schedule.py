#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
This utility provides access to 
'''

# Default starting and ending times for classes / searches
TIME_END = '2359'
TIME_START = '0000'

class InvalidCourseData(Exception): pass

class Courses:
    from typing import Iterable
    
    _data: list
    
    def __init__(self, data: list = None) -> None:
        self.data = data
    
    @staticmethod
    def _verify(data) -> bool:
        # Verify that the data is a list of rooms
        for course in data:
            if not course.get('courseTitle'):
                return False
        return True

    @property
    def data(self) -> list:
        return self._data
    
    @data.setter
    def data(self, data: list):
        if Courses._verify(data):
            self._data = data
        else:
            raise InvalidCourseData("Invalid course provided")
    
    def classes_in_room(self, buildings: list = None, rooms: list = None):
        '''
        Returns a count of how many classes are in the specified room(s)
        '''
        counts: dict = {}
        for course in self.data:
            for mF in course.get('meetingsFaculty', []):
                # Gather some initial information about the course/room
                times: dict = mF.get('meetingTime', {})
                course_building: str = times.get("building", "")
                course_room: str = times.get("room", "")
                if not course_building:
                    course_building = "Online"
                    course_room = ""
                room_id: str = f'{course_building}-{course_room}'
                
                # Match the building and room number
                if (
                    (not buildings or course_building in buildings)
                    and
                    (not rooms or course_room in rooms)
                ):
                    if room_id not in counts:
                        counts[room_id] = 1
                    else:
                        counts[room_id] += 1
        # Sort by number of classes in each room
        counts_sorted: list = list(counts.items())
        return sorted(counts_sorted, key = lambda x: x[1])

    def get_schedules(self,
        buildings: list = None,
        rooms: list = None,
        days: Iterable = None,
        start: str = TIME_START,
        end: str = TIME_END,
        free: bool = False
    ):
        '''
        Search for rooms and their schedules.
        '''
        matches: list = []
        invalid_rooms: set = set()
        for course in self.data:
            for mF in course.get('meetingsFaculty', []):
                # Gather some initial information about the course/room
                times: dict = mF.get('meetingTime', {})
                course_building: str = times.get("building", "")
                course_room: str = times.get("room", "")
                if not course_building:
                    course_building = "Online"
                    course_room = ""
                room_id: str = f'{course_building}-{course_room}'
                prof: dict = course.get('faculty', [])
                prof_str: str = ""
                if prof:
                    prof = prof[0]
                    prof_str: str = prof.get('displayName')
                    prof_email: str = prof.get('emailAddress')
                    if prof_str:
                        prof_str += f' <{prof_email}>'
                    else:
                        prof_str = prof_email
                else:
                    pass
                
                course_start: str = times.get('beginTime') or TIME_START
                course_end: str = times.get('endTime') or TIME_END
                # Match the building and room number
                if (
                    (not buildings or course_building in buildings)
                    and
                    (not rooms or course_room in rooms)
                ):
                    # A string of the meeting days
                    course_days: str = "".join([
                        "U" if times.get('sunday') else '',
                        "M" if times.get('monday') else '',
                        "T" if times.get('tuesday') else '',
                        "W" if times.get('wednesday') else '',
                        "R" if times.get('thursday') else '',
                        "F" if times.get('friday') else '',
                        "S" if times.get('saturday') else '',
                    ])
                    
                    # If a day is specified, ensure that this course meets on
                    # that day. valid_day is initially set to True if no days
                    # are specified and False if days are specified
                    valid_day: bool = not bool(days)
                    if days:
                        for day in days:
                            if day.upper() in course_days:
                                valid_day = True
                    
                    # Ensure that the room time matches the requested times
                    valid_time: bool = False
                    if free and valid_day:
                        # Make sure neither the start nor the end time is in
                        # between the specified times
                        if (
                            not (start < course_start < end)
                            and
                            not (start < course_end < end)
                        ):
                            valid_time = True
                        else:
                            invalid_rooms.add(room_id)
                    elif valid_day:
                        # Make sure either the start or the end time is in
                        # between the specified times
                        if (
                            (start < course_start < end)
                            or
                            (start < course_end < end)
                        ):
                            valid_time = True
                        else:
                            invalid_rooms.add(room_id)
                    
                    if valid_day and valid_time:
                        days_list: list = [
                            times.get('sunday'),
                            times.get('monday'),
                            times.get('tuesday'),
                            times.get('wednesday'),
                            times.get('thursday'),
                            times.get('friday'),
                            times.get('saturday'),
                        ]
                        info: dict = {
                            'room': room_id,
                            'days': course_days,
                            'days_list': days_list,
                            'time_start': times.get('beginTime') or '',
                            'time_end': times.get('endTime') or '',
                            'title': course.get('courseTitle') or 'No Course Name',
                            'professor': prof_str
                        }
                        matches.append(info)
        # Remove any invalid rooms
        return [x for x in matches if x['room'] not in invalid_rooms]

def _run():
    import json
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-b", "--building", action="append",
        help="Specify the buildings to search in")
    parser.add_argument("-r", "--room", action="append",
        help="Specify the room numbers to search for")
    parser.add_argument("-d", "--day", action="append",
        help="""Only show schedules for matching days. If used more than once,
        then each day provided will be matched.""")
    parser.add_argument("-s", "--start-time", default=TIME_START,
        help="The beginning of a time range to search for.")
    parser.add_argument("-e", "--end-time", default=TIME_END,
        help="The end of a time range to search for.")
    parser.add_argument("-f", "--free", action="store_true",
        help="""Instead of searching for rooms' schedules, search for rooms
        that are free during the specified time range.""")
    parser.add_argument("-p", "--professor", action="store_true",
        help="""Show the professor for the specified class.""")
    parser.add_argument("files", nargs="+",
        help="JSON files with course information")
    parser.epilog = __doc__
    options: argparse.Namespace = parser.parse_args()
    
    course_data: list = []
    for filepath in options.files:
        try:
            j = json.load(open(filepath))
            course_data.extend(j)
        except InvalidCourseData:
            print(f"Invalid data found in '{filepath}'")
    
    courses: Courses = Courses(course_data)
    
    # Format the search options
    days: list = []
    if options.day:
        days = [str(x).upper()[0] for x in options.day]
    buildings: list = []
    if options.building:
        buildings = [x.upper() for x in options.building]
    
    # Gather the matches
    matches: list = courses.get_schedules(
        buildings,
        options.room,
        days,
        options.start_time,
        options.end_time,
        options.free
    )
    
    # If we got matches, print the infoz
    if len(matches) > 0:
        # Sort first by room, then day, then time, then course name
        matches = sorted(matches, 
            key=lambda x: (
                x['room'],
                list(reversed(x['days_list'])),
                x['time_start'],
                x['title']
            )
        )
        
        # Print coluumn headers
        print('{:<10}'.format("Room"), end=" ")
        print('{:<10}'.format("Days"), end=" ")
        print('{:<10}'.format("Time"), end="   ")
        if options.professor:
            print('{:<40}'.format("Professor"), end=" ")
        print("Course")
        
        for course in matches:
            print('{:<10}'.format(course.get('room', '')), end=" ")
            print('{:<10}'.format(course.get('days'), ''), end=" ")
            print('{:<4}'.format(course.get('time_start', '')), end="-")
            print('{:<4}'.format(course.get('time_end', '')), end="    ")
            if options.professor:
                print('{:<40}'.format(course.get('professor', '')), end=" ")
            print(course.get('title'))

if __name__ == '__main__':
    _run()