#coding=utf8

from grab import Grab
import hashlib

class InfoParser():

	def __init__(self, selectors):
		self.selectors = selectors

	def pr_search(self, str, n):
		return '1' if str.find(n) >= 0 else '0'

	def pr_price(self, str):
		for s in str.split():
			if s[0] == '$':
				s = s[1:]
			try:
				return float(s)
			except:
				continue
		return None

	def get_info(self, url):
		if len(self.selectors) == 0:
			raise Exception("To configurate selectors")
		
		try:
			grab = Grab()
			grab.go(url)
		except:
			raise Exception('Error grab url "%s"' % url)
		
		return self.parse_info(grab)

	def parse_value(self, grab, selector):
		try:
			elem = grab.doc.select(selector['path'])
		except Exception as e:
			raise Exception('Error in selector %s' % str(e))

		if selector['type'] == 'exist':
			return  '1' if len(elem) > 0 else '0'

		if len(elem) == 0:
			raise Exception('Selector dont found')
			
		# удаляем пробелы лишние
		if selector['type'] == 'text':
			value = elem[0].text().strip()
		elif selector['type'].startswith('attr'):
			value = elem[0].attr(selector['type'][5:]).strip()
		
		if 'parser' in selector:
			ps = selector['parser'].split('@')
			if ps[0] == 'url':
				value = grab.make_url_absolute(value)
			else:
				value = getattr(self, 'pr_'+ps[0])(value, *ps[1:])
			value = unicode(value)
		
		return value

	def parse_info(self, grab):
		info = dict() 
		for key,selector in self.selectors.items():
			try:
				if 'path' not in selector:
					raise Exception('path error')
				value = self.parse_value(grab, selector)
			except Exception as e:
				if selector['required'] == '1':
					raise Exception('Error grab for key "%s": %s' % (key, str(e)))
				else:
					value = ''

			info[key] = value
		return info

