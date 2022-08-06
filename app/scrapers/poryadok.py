import os
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


class PoryadokSpider(scrapy.Spider):
    name = "poryadok"

    def __init__(self, url=None, path=None):
        self.url = url
        self.path = path

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse)

    def parse(self, response):
        # print(response.css('span.trigger-text::text').get().strip())
        links = response.css('div.catalog-product-inner-wrap').xpath('a/@href')
        for link in links[:1]:
            time.sleep(random.randint(1, 5))
            yield response.follow(link.get(), callback=self.parse_item)

        pages = response.css('li.list__item').getall()
        current_page = next(i for i, n in enumerate(pages) if 'Текущая страница' in n)
        try:
            next_page = response.css('li.list__item')[current_page+1].xpath('a/@href').get()
            next_page = 'https://spb.poryadok.ru' + next_page
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        except:
            pass


    def parse_item(self, response):
        # print(response.css('span.trigger-text::text').get().strip())
        item = OrderedDict()
        name = response.css('div.col-12').xpath('h1/text()').get().strip()
        item['Название'] = name
        item['Ссылка'] = response.url
        picture_link = 'https:' + response.css('div.img img::attr(src)').get()
        picture_name = picture_link.split('/')[-1]
        try:
            directory = self.path
            urllib.request.urlretrieve(picture_link, os.path.join(directory, picture_name))
        except Exception as e:
            print(e)
        item['Название изображения'] = picture_name
        item['Изображение'] = picture_link

        try:
            price_active = response.css('div.price::text').get().strip()
            item['Актуальная цена'] = int(remove_spaces(price_active))
            price_old = response.css('div.price--old::text').get().strip()
            if price_old is not None:
                item['Старая цена'] = int(remove_spaces(price_old))
        except:
            pass

        try:
            attributes = response.css('ul.props').xpath('li')
            for attribute in attributes:
                attr_name = attribute.xpath('div[1]/span/text()').get()
                attr_value = attribute.xpath('div[2]/a/text()').get()
                if attr_value is None:
                    attr_value = attribute.xpath('div[2]/text()').get()
                item[str(attr_name).strip()] = str(attr_value).strip()
        except:
            pass

        yield item


def parse_poryadok(url, user_id):
    path = 'data_{}'.format(user_id)
    pagename = url.strip("/").split("/")[-1]
    filename = os.path.join(path, '{}_poryadok_{}_{}.csv'.format(date.today().strftime("%Y-%m-%d"), pagename, user_id))
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
    process.crawl(PoryadokSpider, url=url, path=path)
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
    url = 'https://spb.poryadok.ru/catalog/osvezhiteli_vozdukha/'
    user_id = '511002883'
    parse_poryadok(url, user_id)
