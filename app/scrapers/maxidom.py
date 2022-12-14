import os
import sys
import urllib
from collections import OrderedDict
from datetime import date

import scrapy
from scrapy.crawler import CrawlerProcess
import time
import random
import pandas as pd


def remove_spaces(string):
    return int(''.join(filter(str.isdigit, string)))


class MaxidomSpider(scrapy.Spider):
    name = "maxidom"

    def __init__(self, url=None, path=None):
        self.url = url
        self.path = path

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse, cookies={'MAXI_LOC_ID': '2'})

    def parse(self, response):
        # print(response.css('span.trigger-text::text').get().strip())
        links = response.css('div.caption-list').xpath('a/@href')
        for link in links:
            time.sleep(random.randint(1, 5))
            yield response.follow(link.get(), callback=self.parse_item, cookies={'MAXI_LOC_ID': '2'})

        next_page = response.css('aside.pager-catalogue').xpath('div/a/@href').getall()[-1]

        if next_page is not None:
            next_page = 'https://maxidom.ru' + next_page
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, cookies={'MAXI_LOC_ID': '2'})

    def parse_item(self, response):
        # print(response.css('span.trigger-text::text').get().strip())
        item = OrderedDict()
        name = response.css('h2.name-product::text').get().strip()
        item['Название'] = name
        item['Ссылка'] = response.url
        picture_link = 'https://maxidom.ru' + response.css('div.slide a::attr(href)').get().split('?')[0]
        picture_name = picture_link.split('/')[-1]
        try:
            directory = self.path
            urllib.request.urlretrieve(picture_link, os.path.join(directory, picture_name))
        except:
            pass
        item['Название изображения'] = picture_name
        item['Изображение'] = picture_link

        try:
            price_active = response.css('div.price-big').xpath('div/text()').get().strip()
            item['Актуальная цена'] = int(remove_spaces(price_active))
            price_old = response.css('div.price-old::text').get().strip()
            if price_old is not None:
                item['Старая цена'] = int(remove_spaces(price_old))
        except:
            pass

        try:
            attributes = response.css('div.tab-row')
            for attribute in attributes:
                attr_name = attribute.xpath('span[1]/text()').get()
                attr_value = attribute.xpath('span[2]/text()').get()
                item[str(attr_name).strip()] = str(attr_value).strip()
        except:
            pass

        yield item


def parse_maxidom(url, user_id):
    path = 'data_{}'.format(user_id)
    pagename = url.strip("/").split("/")[-1]
    filename = os.path.join(path, '{}_maxidom_{}_{}.csv'.format(date.today().strftime("%Y-%m-%d"), pagename, user_id))
    # sys.exit()
    settings = dict(
        USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 OPR/75.0.3969.149',
        AUTOTHROTTLE_ENABLED=True,
        AUTOTHROTTLE_START_DELAY=0.25,
        AUTOTHROTTLE_MAX_DELAY=3,
        FEED_FORMAT="csv",
        FEED_URI=filename
    )
    process = CrawlerProcess(settings)
    process.crawl(MaxidomSpider, url=url, path=path)
    process.start()
    process.stop()
    file_stats = os.stat(filename)
    if file_stats.st_size < 2:
        raise Exception('Scraper failed')
    else:
        csvfile = pd.read_csv(filename)
        csvfile.to_excel(filename.replace('csv', 'xlsx'), sheet_name='Sheet1', index=False)
        return path


if __name__ == "__main__":
    url = sys.argv[1]
    user_id = sys.argv[2]
    print(parse_maxidom(url, user_id))
    # url = 'https://www.maxidom.ru/catalog/osvezhiteli-vozduha/'
    # user_id = '511002883'
    # parse_maxidom(url, user_id)
