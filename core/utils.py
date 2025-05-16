import datetime
import calendar
from datetime import datetime as dtime, date, time


def add_months(source_date: datetime.date, months: int) -> datetime.date:
    """
    Adds a months relative to the current date to the end date.
    :param source_date:
    :param months:
    :return:
    """
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def last_day(year: int, month: int) -> int:
    """
    Returns the last day of the month.
    :param year:
    :param month:
    :return:
    """
    day = calendar.monthrange(year, month)[1]
    return day


class EventCalendar(calendar.LocaleHTMLCalendar):
    def __init__(self, events=None):
        super(EventCalendar, self).__init__()
        self.events = events

    def formatday(self, day, weekday, events):
        """
        Return a day as a table cell.
        """
        events_html = ''
        if day in events:
            events_from_day = events[day]
            events_html = "<ul>"
            for event in events_from_day:
                events_html += event.calendar_text() + "<br>"
            events_html += "</ul>"

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s">%d%s</td>' % (self.cssclasses[weekday], day, events_html)

    def formatweek(self, theweek, events):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, events) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        events = self.events or []
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, events))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)