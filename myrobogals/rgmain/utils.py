import datetime
import re
from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

__all__ = ('SelectDateWidget', 'email_re')

email_re = re.compile(
	r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
	# quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
	r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
	r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
	r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class SelectDateWidget(Widget):
	"""
	A Widget that splits date input into three <select> boxes.

	This also serves as an example of a Widget that has more than one HTML
	element and hence implements value_from_datadict.
	"""
	none_value = (0, '---')
	day_field = '%s_day'
	month_field = '%s_month'
	year_field = '%s_year'

	def __init__(self, attrs=None, years=None, required=True):
		# years is an optional list/tuple of years to use in the "year" select box.
		self.attrs = attrs or {}
		self.required = required
		if years:
			self.years = years
		else:
			this_year = datetime.date.today().year
			self.years = range(this_year-100, this_year+10)

	def render(self, name, value, attrs=None):
		try:
			year_val, month_val, day_val = value.year, value.month, value.day
		except AttributeError:
			year_val = month_val = day_val = None
			if isinstance(value, basestring):
				match = RE_DATE.match(value)
				if match:
					year_val, month_val, day_val = [int(v) for v in match.groups()]

		output = []

		if 'id' in self.attrs:
			id_ = self.attrs['id']
		else:
			id_ = 'id_%s' % name

		local_attrs = self.build_attrs(id=self.day_field % id_)
		day_choices = [(i, i) for i in range(1, 32)]
		if not (self.required and value):
			day_choices.insert(0, self.none_value)
		s = Select(choices=day_choices)
		select_html = s.render(self.day_field % name, day_val, local_attrs)
		output.append(select_html)

		month_choices = MONTHS.items()
		if not (self.required and value):
			month_choices.append(self.none_value)
		month_choices.sort()
		local_attrs['id'] = self.month_field % id_
		s = Select(choices=month_choices)
		select_html = s.render(self.month_field % name, month_val, local_attrs)
		output.append(select_html)

		year_choices = [(i, i) for i in self.years]
		if not (self.required and value):
			year_choices.insert(0, self.none_value)
		local_attrs['id'] = self.year_field % id_
		s = Select(choices=year_choices)
		select_html = s.render(self.year_field % name, year_val, local_attrs)
		output.append(select_html)

		return mark_safe(u'\n'.join(output))

	def id_for_label(self, id_):
		return '%s_month' % id_
	id_for_label = classmethod(id_for_label)

	def value_from_datadict(self, data, files, name):
		y = data.get(self.year_field % name)
		m = data.get(self.month_field % name)
		d = data.get(self.day_field % name)
		if y == m == d == "0":
			return None
		if y and m and d:
			return '%s-%s-%s' % (y, m, d)
		return data.get(name, None)

RE_TIME = re.compile(r'(\d\d?):(\d\d?):00$')

class SelectTimeWidget(Widget):
	none_value = (0, '---')
	hour_field = '%s_hour'
	minute_field = '%s_minute'

	def __init__(self, attrs=None, required=True):
		self.attrs = attrs or {}
		self.required = required

	def render(self, name, value, attrs=None):
		try:
			hour_val, minute_val = value.hour, value.minute
		except AttributeError:
			hour_val = minute_val = None
			if isinstance(value, basestring):
				match = RE_TIME.match(value)
				if match:
					hour_val, minute_val = [int(v) for v in match.groups()]

		output = []

		if 'id' in self.attrs:
			id_ = self.attrs['id']
		else:
			id_ = 'id_%s' % name

		hour_choices = [(i, '%02d' % i) for i in range(0, 24)]
		if not (self.required and value):
			hour_choices.append(self.none_value)
		s = Select(choices=hour_choices)
		select_html = s.render(self.hour_field % name, hour_val)
		output.append(select_html)

		output.append(':')

		minute_choices = [(i, '%02d' % i) for i in range(0, 60)]
		if not (self.required and value):
			minute_choices.append(self.none_value)
		s = Select(choices=minute_choices)
		select_html = s.render(self.minute_field % name, minute_val)
		output.append(select_html)

		return mark_safe(u'\n'.join(output))

	def id_for_label(self, id_):
		return '%s_hour' % id_
	id_for_label = classmethod(id_for_label)

	def value_from_datadict(self, data, files, name):
		h = data.get(self.hour_field % name)
		m = data.get(self.minute_field % name)
		if h == "24" or m == "60":
			return None
		if h and m:
			return '%s:%s:00' % (h, m)
		return data.get(name, None)
