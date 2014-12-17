#coding=utf

import re

class ProductMatcher:
	def tofloat(self, str):
		try:
			str = re.findall(r"[-+]?[\d| ]*[\.|,]\d+|[\d| ]+", str)[0]
			str = str.replace(" ", "")
			str = str.replace(",", ".")
			return float(str)
		except:
			return None

	def get_sims(self, p1, p2):
		s1 = self.get_signs(p1)
		s2 = self.get_signs(p2)
		return self.get_sim(s1,s2)
		
	def get_signs(self, p):
		res = {}

		# разделяем числа 
		res['digits'] = set()
		for key in ['name', 'packing']:
			if p and key in p.keys():
				ws = re.sub(ur'[^0-9,\. ]+', '', p[key])
				
				for w in ws.split():
					d = self.tofloat(w)
					if d:
						res['digits'].add(d)
				
		# список ключевых слов
		res['words'] = set()
		for key in ['name', 'brand', 'category']:
			res['w'+key] = set()
			if key in p and p[key]:
				#ws = p[key].decode('utf-8').lower()
				ws = p[key].lower()
				ws = re.sub(ur'[^A-Za-zА-Яа-я ]+', '', ws)
				
				for w in ws.split():
					if len(w) > 1:
						res['words'].add(w)
						res['w'+key].add(w)

		return res

	def get_sim(self, p1, p2):
		sw = len(p1['words'] & p2['words'])
		pw = float(len(p1['words'] | p2['words']))
		
		sb = len(p1['wbrand'] & p2['wbrand'])
		pb = float(len(p1['wbrand'] | p2['wbrand']))
		
		# sc = len(p1['wcategory'] & p2['wcategory'])
		# pc = float(len(p1['wcategory'] | p2['wcategory']))
		
		sn = len(p1['wname'] & p2['wname'])
		pn = float(len(p1['wname'] | p2['wname']))
		
		sd = 0
		pd = float(len(p1['digits'] | p2['digits']))
		for d1 in p1['digits']:
			for d2 in p2['digits']:
				t = abs(d1-d2)/((d1+d2)/2)
				if t < 0.1:
					sd += (1-t)*(1-t)
		
		return 0.3 * (sw/pw) + \
			0.3 * (sn/pn) + \
			0.25 * (sb/pb) + \
			0.25 * (sd/pd)

	def ordering(self, matches, reverse=False):
		if len(matches):
			import operator
			return [k for k,v in sorted(matches.items(), key=operator.itemgetter(1), reverse=reverse)]
		else:
			return []


	def matching(self, product, products, min_sim = 0.45, min_count=10):
		# вычисляем признаки
		orig_signs = self.get_signs(product)
		products_signs = {}
		
		selected = []
		for i,p in products.items():
			products_signs[i] = self.get_signs(p)
			selected.append(i)
		
		# отбор
		matches = {}
		for i in selected:
			matches[i] = self.get_sim(orig_signs, products_signs[i])

		selected = self.ordering(matches,reverse=True)
		
		res = []
		for ind in selected:
			if matches[ind] < min_sim and len(res) >= min_count:
				break
			res.append(ind)
		return res