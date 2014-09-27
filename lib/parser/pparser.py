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
            print "To configurate selectors"
            return None
        try:
            grab = Grab()
            grab.go(url)
        except:
            print 'Error grab url',url
            return None

        return self.parse_info(grab)

    def parse_value(self, grab, selector):
        try:
            elem = grab.doc.select(selector['path'])
        except:
            return None    

        if selector['type'] == 'exist':
            return  '1' if len(elem) > 0 else '0'

        if len(elem) == 0:
            return None
            
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
            value = self.parse_value(grab, selector)
            
            if value is None:
                if selector['required'] == '1':
                    print 'Error grab for key "%s"' % key
                    return None
                else:
                    value = ''

            info[key] = value
        return info

