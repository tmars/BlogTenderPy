#codinf=utf8

from pparser import InfoParser
from spider import ScanSpider, UpdateSpider
import logging, json

def merge(a, b, path=None):
	"merges b into a"
	if path is None: path = []
	for key in b:
		if key in a:
			if isinstance(a[key], dict) and isinstance(b[key], dict):
				merge(a[key], b[key], path + [str(key)])
			elif a[key] == b[key]:
				pass # same leaf value
			else:
				raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
		else:
			a[key] = b[key]
	return a


class ProductParser():
	data_keys = ['url', 'name', 'image', 'price', 'available']

	def __init__(self, host, selectors):
		c = {
			'name': {'required': '1'},
			'price': {'parser': 'price', 'required': '1'},
			'image': {'parser': 'url', 'required': '0'},
			'available': {'required': '0'},
			'brand': {'required': '0'},
			'category': {'required': '0'},
		};
		self.selectors = merge(selectors, c)
		self.host = host

	def update(self, urls):
		logging.basicConfig(level=logging.DEBUG)

		parser = InfoParser({
			'price': self.selectors['price'],
			'available': self.selectors['available'],
		})
		spider = UpdateSpider(urls=urls, parser=parser, thread_number=1)
		spider.run()
		
		return spider.info_list, ['url', 'price', 'available']

	def scan(self, excludes=[]):
		logging.basicConfig(level=logging.DEBUG)

		parser = InfoParser(self.selectors)
		spider = ScanSpider(host=self.host, parser=parser, thread_number=1, excludes=excludes)
		spider.run()

		infos = spider.info_list
		keys = []
		if len(infos):
			keys = self.data_keys + [k for k in infos[0].keys() if k not in self.data_keys]
		urls = spider.passed_urls
		
		return infos, keys, urls
		
	def find(self, url):
		parser = InfoParser(self.selectors)
		return parser.get_info(url)

	def pack(data):
		ks = ['url', 'name', 'image', 'price', 'available']
		res = []
		for d in data:
			try:
				r = dict()
				r['name'] = d['name'] 
				r['url'] = d['url'] 
				r['image'] = d['image']
				r['price'] = float(d['price'])
				r['available'] = int(d['available']) if d['available'] else None
				r['additional'] = json.dumps({k:v for k,v in d.items() if k not in ks}, ensure_ascii=False)
				res.append(r)
			except:
				pass
		return res

	pack = staticmethod(pack)