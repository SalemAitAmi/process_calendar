""" Contains the process_cal classs
"""
import re
import datetime as dt

class process_cal:
    """ Constructor: Takes 1 filename as a parameter
        Summary: Processes an ICS file, such that events are more easily accessed
    """
    def __init__(self, filename):
        self.filename = filename
    
    def get_events_for_day(self, cur_dt):
        """ Parameters: 1 Parameter; valid datetime object
        Summary: Opens an ICS file and retrieves all events that occur on the same date as cur_dt
        Return: A formatted string containing all events 
        """
        if cur_dt.year == 0 or cur_dt.month == 0 or cur_dt.day == 0:
            return None
        
        file = open(self.filename).read()
        parsed_by_event = re.split('BEGIN:VEVENT\n', file)
        events_today_list = []
        events_today_str = dt.datetime.strftime(cur_dt, '%B %d, %Y (%a)') + '\n'
        hyphens = '---------------------------------------------------------------'
        events_today_str += hyphens[:len(events_today_str)-1]
        events_today_str += '\n'
        
        for event_raw in parsed_by_event:
            if re.search('RRULE:', event_raw) == None:
                event_tup = self.process_event(event_raw)
                if event_tup != None:
                    if event_tup[0].date()-cur_dt.date() == dt.timedelta(days=0):
                        events_today_list.append(event_tup)

            elif re.search('RRULE:', event_raw) != None:
                pattern_RRULE = re.compile(r'RRULE:\S+UNTIL=([0-9]+)T([0-9]+)\S+')
                event_tup = self.process_event(event_raw)
                raw_until = pattern_RRULE.search(event_raw)
                until = dt.datetime.strptime(pattern_RRULE.sub(r'\1\2', raw_until.group()), '%Y%m%d%H%M%S')
                event_iter_in_range = self.handle_RRULE(cur_dt, event_tup, until)
                if event_iter_in_range != None:
                    events_today_list.append(event_iter_in_range)

        events_today_list.sort()
        for event in events_today_list:
            events_today_str += self.event_to_fstr(event, events_today_str)

        if events_today_str[len(events_today_str)-1] != '\n':
            return events_today_str
        
    def event_to_fstr(self, event_tup, events_today):
        """ Parameters: 2 Parameters; an event tuple, a string
        Summary: Converts an event tuple into a formatted string
        Return: A formatted string
        """
        if events_today[len(events_today)-1] == '\n':
            event_fstr = ''
        else:
            event_fstr = '\n'
        start = dt.datetime.strftime(event_tup[0], '%I:%M %p ')    #Start time
        if start[0] == '0':
            start = ' '+start[1:]
        event_fstr += start
        event_fstr += 'to '    
        end = dt.datetime.strftime(event_tup[1], '%I:%M %p')    #End time
        if end[0] == '0':
            end = ' '+end[1:]
        event_fstr += end
        event_fstr += ': '
        event_fstr += event_tup[3]  #Summary
        event_fstr += ' {{'
        event_fstr += event_tup[2]
        event_fstr += '}}'

        return event_fstr

    def handle_RRULE(self, cur_dt, event_tup, until_dt):
        """ Parameters: 3 Parameters; a datetime object, an event tuple, a datetime object
        Summary: Handles repetition when applicable. Increments an event's start date to see if any iteration has the same date as cur_dt.
        Return: If an iterration has the same date as cur_dt, returns an event tuple, otherwise, returns None
        """
        start = event_tup[0]
        end = event_tup[1]

        if start.date() > cur_dt.date() or until_dt.date() < cur_dt.date():
            return None
        elif start.date() == cur_dt.date():
            start = start.replace(year= cur_dt.year, month= cur_dt.month, day= cur_dt.day)
            end = end.replace(year= cur_dt.year, month= cur_dt.month, day= cur_dt.day)
            rep_tup = (start, end, event_tup[2], event_tup[3])
            return rep_tup
    
        while(start <= cur_dt and start <= until_dt ):
            start += dt.timedelta(days=7)
            if(start.date() == cur_dt.date()):
                start = start.replace(year= cur_dt.year, month= cur_dt.month, day= cur_dt.day)
                end = end.replace(year= cur_dt.year, month= cur_dt.month, day= cur_dt.day)
                rep_tup = (start, end, event_tup[2], event_tup[3])
                return rep_tup

        return None

    def process_event(self, event):
        """ Parameters: 1 Parameter; an event tuple
        Summary: Extracts information from a raw event and stroes it in a tuple
        Return: If all the necessary fileds are present, returns a tuple, otherwise, returns None
        """
        pattern_DTSTART = re.compile(r'DTSTART:([0-9]+)T([0-9]+)')
        pattern_DTEND = re.compile(r'DTEND:([0-9]+)T([0-9]+)')
        pattern_LOCATION = re.compile(r'LOCATION:([^\n]+)')
        pattern_SUMMARY = re.compile(r'SUMMARY:([^\n]+)')
        
        raw_dtstart = pattern_DTSTART.search(event)
        raw_dtend = pattern_DTEND.search(event)
        raw_location = pattern_LOCATION.search(event)
        raw_summary = pattern_SUMMARY.search(event)

        if (raw_dtstart != None) and (raw_dtend != None) and (raw_location != None) and (raw_summary != None):
            dtstart = dt.datetime.strptime(pattern_DTSTART.sub(r'\1\2', raw_dtstart.group()), '%Y%m%d%H%M%S')
            dtend = dt.datetime.strptime(pattern_DTEND.sub(r'\1\2', raw_dtend.group()), '%Y%m%d%H%M%S')
            location = pattern_LOCATION.sub(r'\1', raw_location.group())
            summary = pattern_SUMMARY.sub(r'\1', raw_summary.group())
            event_tup = (dtstart, dtend, location, summary)
            return event_tup
        elif (raw_dtstart != None) and (raw_dtend != None) and (raw_summary != None):
            dtstart = dt.datetime.strptime(pattern_DTSTART.sub(r'\1\2', raw_dtstart.group()), '%Y%m%d%H%M%S')
            dtend = dt.datetime.strptime(pattern_DTEND.sub(r'\1\2', raw_dtend.group()), '%Y%m%d%H%M%S')
            location = ''
            summary = pattern_SUMMARY.sub(r'\1', raw_summary.group())
            event_tup = (dtstart, dtend, location, summary)
            return event_tup

        return None