from __future__ import absolute_import
import scrapy
import datetime
import re
from school_info.items import *
import urlparse
from scrapy.http.request import Request
import re
from bs4 import BeautifulSoup as BS

class FaultySpider(scrapy.Spider):
    name = "faulty"
    # def start_requests(self):
    base_url = 'https://directory.engr.wisc.edu/bme/Faculty/'
    start_urls = ['https://directory.engr.wisc.edu/bme/Faculty/']

    def parse(self, response):
        if response.url == self.base_url:
            name_list = self.get_fulty_names(response)
            name_list = list(set(name_list))
            for name in name_list:
                name = name.split("/")[-2]
                url = urlparse.urljoin(response.url,name)
                yield Request(url)
        else:    
            item = self.get_detail(response)
            yield item


    def get_fulty_names(self, response):
        name_list = response.xpath('//div[contains(@class,"content padded-content")]').xpath('//div[contains(@class,"profileText")]').xpath('//a[contains(@class,"display")]/@href').extract()
        return name_list

    def get_detail(self, response):
        item = FaultyItem()

        item['email'] = response.xpath('//a[contains(@href,"mailto")]/text()').extract_first()
    
            
        item['name'] = response.xpath('//p[contains(@class,"newProfile")]/text()').extract_first()
        item['phone'] = self.fetch_phone(response)

        item['title'] = response.xpath('//div[contains(@class, "side-nav col-sm-3")]/p/b/text()').extract_first()
        item['link'] = response.url
        item['img'] = response.xpath('//img[contains(@alt,"Profile Photo")]/@src').extract_first()

        item['background'] = self.fecth_background(response)

        item['location'] = response.xpath('//div[contains(@class,"newThreeColCenter")]/p')[0].extract().replace("<br>", ",").replace("<p>","").replace("</p","")
        return item

    def fetch_phone(self, response):
        match = re.search(r"Ph:[' ']*(.*)<br>Fax", response.body)
        if match:
            return re.search(r"Ph:[' ']*(.*)<br>Fax", response.body).group(1)
        else:
            return ''

    def fecth_background(self, response):

        script = ''.join(response.xpath("//script").extract())
        match = re.search('tabNum == 1(.*)tabNum == 2', script)
        if match:    
            html = BS(match.group(0))
            li_list = html.findAll('li')
        else:
            return ""
        background = ''
        print li_list
        info = []
        if li_list:
            for li in li_list:
                info.append(li.text)
            return ','.join(info)
        else:
            return ""
