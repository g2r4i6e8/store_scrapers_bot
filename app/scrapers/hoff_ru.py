# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 21:33:30 2021

@author: kolom
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from selenium.webdriver.common.by import By
from tqdm import tqdm
import re
import pandas as pd
import os
import requests
from collections import OrderedDict
from datetime import date

def remove_spaces(string):
    return (re.sub(' ','',string))

def download_image(picture_link, picture_name, path):
    directory = os.path.join(path, 'images')
    if not os.path.exists(directory):
        os.makedirs(directory)

    request = requests.get(picture_link)
    if request.status_code == 200:
        with open(os.path.join(directory,picture_name), 'wb') as f:
            f.write(request.content)

def parse_hoff(url, path):
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 OPR/75.0.3969.149")

    driver = webdriver.Chrome(r"C:\Users\kolom\OneDrive\Documents\Projects\store_scrapers_bot\chromedriver\chromedriver.exe", options=opts)

    # basepage = 'https://hoff.ru/catalog/tovary_dlya_doma/posuda/servirovka_stola/stolovye_pribory/' #тест
    basepage = url
    driver.get(basepage)
    # pagename = driver.find_element(by=By.CLASS_NAME, value='page-title').text
    # pages = int(driver.find_element(by=By.CLASS_NAME, value='pagination').find_elements(by=By.XPATH, value='a')[-1].text)
    pages = 1

    links = []
    pbar = tqdm(total = pages)
    for i in range(1,pages+1):
        page = '{}page{}'.format(basepage, i)
        driver.get(page)
        time.sleep(0.5)
        items = driver.find_elements(by=By.CLASS_NAME, value = 'product-card')
        print(items)
        links.extend([a.get_attribute("href") for a in items])
        pbar.update(1)
    pbar.close()

    print(links)

    data = []
    pbar1 = tqdm(total = len(links))
    for link in links:
        item = OrderedDict()
        driver.get(link)
        name = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[1]/h1').text.split('#')[0]
        item['Название'] = name
        item['Ссылка'] = link
        try:
            picture_link = driver.find_element_by_class_name('image-popup-no-margins').get_attribute("data-src")
            picture_name = picture_link.split('/')[-1]
            download_image(picture_link, picture_name, path)
            item['Название изображения'] = picture_name
            item['Изображение'] = ''
        except:
            pass
        rub_normal = int(remove_spaces(driver.find_element_by_class_name('price-current').text.replace('P','')))
        item['Обычная цена'] = rub_normal
        try:
            rub_sale = int(remove_spaces(driver.find_element_by_class_name('discount-info').find_element_by_xpath('div[1]/span[1]').text))
            item['Акционная цена'] = rub_sale
        except:
            pass

        attributes = driver.find_elements_by_class_name('single-param')
        for attribute in attributes:
            atr_name = attribute.find_element_by_xpath('div[1]/span').text.replace(':','')
            try:
                atr_value = attribute.find_element_by_xpath('div[2]/span').text
                item[atr_name] = atr_value
            except:
                pass
        data.append(item)
        pbar1.update(1)
        time.sleep(0.5)
    pbar1.close()
    driver.close()

    database = pd.DataFrame(data, columns=data[0].keys())
    filename = '{}_hoff_{}'.format(date.today().strftime("%Y-%m-%d"), pagename)
    database.to_excel(os.path.join(path,'{}.xlsx'.format(filename)), sheet_name='Sheet1', index=False)

if __name__ == '__main__':
    url = 'https://hoff.ru/catalog/tovary_dlya_doma/posuda/servirovka_stola/stolovye_pribory/'
    path = os.path.join('temp', '123')
    parse_hoff(url, path)