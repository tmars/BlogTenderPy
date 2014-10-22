#coding=utf8

from grab.spider import Spider, Task
import urlparse, sys, re, hashlib
from time import sleep

class BaseSpider(Spider):
    def __init__(self, parser, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.parser = parser

class UpdateSpider(BaseSpider):

    def __init__(self, urls, *args, **kwargs):
        super(UpdateSpider, self).__init__(*args, **kwargs)
        self.initial_urls = urls

    def prepare(self):
        self.info_list = list()
    
    def task_initial(self, grab, task):
        info = self.parser.parse_info(grab)
        info['url'] = task.url.decode('utf8')
        self.info_list.append(info)

class ScanSpider(BaseSpider):

    def __init__(self, host, excludes=[], *args, **kwargs):
        super(ScanSpider, self).__init__(*args, **kwargs)
        self.host = host
        self.initial_urls = [host]
        self.hash_keys = [k for k,v in self.parser.selectors.items() if v["required"] == '1']
        self.excludes = excludes

    def prepare(self):
        self.infos = dict()
        self.old_urls = set()
        self.new_urls = set()

    @property
    def info_list(self):
        return self.infos.values()

    @property
    def passed_urls(self):
        return self.old_urls

    def task_initial(self, grab, task):
        self.old_urls.add(task.url)
        
        if grab.response.code != 200:
            if task.task_try_count > 1:
                sleep(task.task_try_count * 0.1)
            
            task = Task('initial', url=grab.config['url'], task_try_count=task.task_try_count + 1, valid_status=task.valid_status)
            self.add_task(task)
            return

        # ищем информацию на странице
        try:
            info = self.parser.parse_info(grab)
        except:
            info = None

        if info:
            info['url'] = task.url
            # исключаем повторения
            m = hashlib.md5()
            for k in self.hash_keys:
                m.update(info[k].encode('utf-8'))
            h = m.hexdigest()
            if h not in self.infos or len(task.url) < len(self.infos[h]['url']):
                self.infos[h] = info
            
        # выборка ссылок
        link = grab.doc.select('//*[@href]')
        for s in link:
            url = s.attr('href')
            try:
                url = grab.make_url_absolute(url)
                self.create_task(url)    
            except:
                continue

    def create_task(self, url):
        if len(url) == 0:
            return

        # отбираем
        if url[-4:] in ['.jpg', '.css', '.png', '.mp3', '.avi', '.svg', '.pdf', '.ico']:
            return

        # преобразование и проверка на домен
        if url.startswith('http') and not url.startswith(self.host):
            return

        # проверяем по исключениям
        for p in self.excludes:
            if re.search(r"%s" % p, url) is not None:
                return

        # убираем параметры
        if '#' in url:
            url = url.split('#')[0]
        #if '?' in url:
        #    url = url.split('?')[0]

        # добавляем в очередь
        if url in self.old_urls:
            return
        if url in self.new_urls:
            return

        self.new_urls.add(url)
        task = Task('initial', 
            url=url, 
            valid_status=(200, 403, 500)
        )
        self.add_task(task)