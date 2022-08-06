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


class LentaSpider(scrapy.Spider):
    name = "lenta"

    def __init__(self, url=None, path=None):
        self.url = url
        self.path = path

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse, cookies={'CityCookie': 'Spb', 'Store': '0011'})

    def parse(self, response):
        print(response.css('div.address-container__address::text').get().strip())
        for link in response.xpath('//a[contains(@href, "/product/")]/@href'):
            time.sleep(random.randint(1, 5))
            yield response.follow(link.get(), callback=self.parse_item, cookies={'CityCookie': 'Spb', 'Store': '0011'})

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse, cookies={'CityCookie': 'Spb', 'Store': '0011'})

    def parse_item(self, response):
        print(response.css('div.address-container__address::text').get().strip())
        item = OrderedDict()
        name = response.css('h1.sku-page__title::text').get().strip()
        item['Название'] = name
        item['Ссылка'] = response.url
        picture_link = response.xpath('//img[contains(@src, "png")]/@src').get().split('?')[0]
        picture_name = picture_link.split('/')[-1]
        # try:
        #     directory = self.path
        #     if not os.path.exists(directory):
        #         os.makedirs(directory)
        #     urllib.request.urlretrieve(picture_link, os.path.join(directory, picture_name))
        # except:
        #     pass
        item['Название изображения'] = picture_name
        item['Изображение'] = picture_link

        try:
            rub_sale = response.css('div.sku-prices-block__item sku-prices-block__item--primary').xpath(
                'div[1]/span[1]').get().strip()
            penny_sale = response.css('div.sku-prices-block__item sku-prices-block__item--primary').xpath(
                'div[1]/small').get().strip()
            item['Акционная цена'] = float(remove_spaces(rub_sale)) + float(remove_spaces(penny_sale)) / 100
        except:
            pass

        try:
            rub_normal = response.css('div.sku-prices-block__item sku-prices-block__item--regular').xpath(
                'div[1]/span[1]').get().strip()
            penny_normal = response.css('div.sku-prices-block__item sku-prices-block__item--regular').xpath(
                'div[1]/small').get().strip()
            item['Обычная цена'] = float(remove_spaces(rub_normal)) + float(remove_spaces(penny_normal)) / 100
        except:
            pass

        try:
            attributes = response.css('div.sku-card-tab-params__item')
            for attribute in attributes:
                attr_name = attribute.xpath('dt/label/text()').get()
                attr_value = attribute.xpath('a/text()').get()
                if attr_value is None:
                    attr_value = attribute.xpath('dd/text()').get()
                item[str(attr_name).strip()] = str(attr_value).strip()
        except:
            pass

        yield item


def parse_lenta(url, user_id):
    path = 'data_{}'.format(user_id)
    pagename = url.strip("/").split("/")[-1]
    filename = os.path.join(path, '{}_lenta_{}_{}.csv'.format(date.today().strftime("%Y-%m-%d"), pagename, user_id))
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
    process.crawl(LentaSpider, url=url, path=path)
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
    url = 'https://lenta.com/catalog/bytovaya-himiya/sredstva-dlya-mytya-posudy/'
    user_id = '511002883'
    parse_lenta(url, user_id)
