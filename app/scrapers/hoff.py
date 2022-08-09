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


class HoffSpider(scrapy.Spider):
    name = "hoff"

    def __init__(self, url=None, path=None):
        self.url = url
        self.path = path

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse, cookies={'current_city': '718'})

    def parse(self, response):
        # print(response.css('span.trigger-text::text').get().strip())
        for link in response.xpath('//a[contains(@href, "/catalog/")]/@href')[:1]:
            time.sleep(random.randint(1, 5))
            yield response.follow(link.get(), callback=self.parse_item, cookies={'current_city': '718'})

        # TODO: pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, cookies={'current_city': '718'})

    def parse_item(self, response):
        # print(response.css('span.trigger-text::text').get().strip())
        item = OrderedDict()
        name = response.css('h1.page-title::text').get().strip()
        item['Название'] = name
        item['Ссылка'] = response.url
        picture_link = response.xpath('//img[contains(@src, "upload")]/@src').get()
        picture_name = picture_link.split('/')[-1]
        try:
            directory = self.path
            urllib.request.urlretrieve(picture_link, os.path.join(directory, picture_name))
        except:
            pass
        item['Название изображения'] = picture_name
        item['Изображение'] = picture_link

        try:
            price_old = response.css('span.product-old-price::text').get().strip()
            if price_old is not None:
                item['Акционная цена'] = int(remove_spaces(price_old))
            price_active = response.css('span.product-price::text').get().strip()
            item['Актуальная цена'] = int(remove_spaces(price_active))
        except:
            pass

        try:
            attributes = response.css('table.product-params-table/tr')
            for attribute in attributes:
                attr_name = attribute.xpath('td[1]/span/text()').get()
                attr_value = attribute.xpath('td[2]/span/a/text()').get()
                if attr_value is None:
                    attr_value = attribute.xpath('td[2]/span/text()').get()
                item[str(attr_name).strip()] = str(attr_value).strip()
        except:
            pass

        yield item


def parse_hoff(url, user_id):
    path = 'data_{}'.format(user_id)
    pagename = url.strip("/").split("/")[-1]
    filename = os.path.join(path, '{}_hoff_{}_{}.csv'.format(date.today().strftime("%Y-%m-%d"), pagename, user_id))
    # sys.exit()
    settings = dict(
        USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.83',
        AUTOTHROTTLE_ENABLED=True,
        AUTOTHROTTLE_START_DELAY=0.25,
        AUTOTHROTTLE_MAX_DELAY=3,
        FEED_FORMAT="csv",
        FEED_URI=filename
    )
    process = CrawlerProcess(settings)
    process.crawl(HoffSpider, url=url, path=path)
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
    url = 'https://hoff.ru/catalog/tovary_dlya_doma/posuda/servirovka_stola/stolovye_pribory/'
    user_id = '511002883'
    parse_hoff(url, user_id)

    # r = requests.get(
    #     'https://hoff.ru/vue/catalog/section/?category_id=1060&limit=30&offset=0&showCount=true&type=product_list')
    # data = r.json()

