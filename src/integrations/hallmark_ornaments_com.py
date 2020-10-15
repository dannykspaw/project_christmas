from os import path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pandas as pd
import time
from csv import reader
import re

from models import products
from utils.selenium import driver

integration_name = path.basename(__file__).replace('.py', '')
COLUMNS = products.columns

action = ActionChains(driver)

# go to website
driver.get(
    "https://www.hallmarkornaments.com/Hallmark-Ornaments-By-Year_c_200.html")

# pull years
year_content_block = driver.find_elements_by_class_name("subcat")

year_links = {}

for year in year_content_block[0:48]:
    year_link = year.get_attribute("href")
    year_num = re.findall(r'\d+', year_link)[0]
    year_links[year_num] = year_link+'?viewall=1'


def __get_ornament_by_url(link):
    driver.get(link)

    # find javascript variable containing product details
    product_location_data = driver.find_element_by_xpath('/html/head/script[7]')
    sku_info_blob = product_location_data.get_attribute('innerText')
    sku_info = sku_info_blob.replace('"', '').replace("' '", '').replace(
        "{", '').replace("var _3d_item =", '').replace("}", '').split('",')

    # prepare javascript var item variable for parsing
    sku_price_split = sku_info[0].split(",price")[1]
    sku_name_code_split = sku_info[0].split(",price")[0]

    # parse into product details
    product_code = sku_name_code_split.split(",id:")[1].split(",name")[0]
    product_name = sku_name_code_split.split("name:")[1]
    product_price = sku_price_split.split(":")[1].split(",availability")[0]
    product_availability = sku_price_split.split("availability:")[1].split(
        ",currency")[0].replace("0", "Not In Stock").replace("1", "In Stock")
    product_brand = "hallmark"
    product_id = sku_name_code_split.split("catalogid:")[1].split(",id")[0]
    product_vendor = integration_name
    product_link = driver.current_url

    product_info = dict.fromkeys(COLUMNS)
    product_info = {
        "sku": product_code,
        "name": product_name,
        "price": product_price,
        "availability": product_availability,
        "brand": product_brand,
        "vendor": product_vendor,
        "link": product_link
    }
    return product_info


def sync_by_url(url):
    return __get_ornament_by_url(url)


def get_ornaments_by_year(year):
    num_of_products = 0
    try:
        year = str(year)
        driver.get(year_links[str(year)])
        quantity = driver.find_element_by_class_name('product-count')
        num_of_products = quantity.text[26:]
    except Exception as err:
        print('unable to get number of ornaments in hallmark_ornaments_com for year {} url {} err {}'.format(year, year_links[str(year)], err))
        year = int(year)
    # create quick view links within year
    quick_view_links = {}
    for x in range(1, int(num_of_products)+1):
        try:
            ornament = driver.find_element_by_xpath(
                '//*[@id="productCategoryBlock"]/div[4]/div/div/div[{}]'.format(str(x)))
            hover = ActionChains(driver).move_to_element(ornament)
            hover.perform()
            content = driver.find_element_by_xpath(
                '//*[@id="productCategoryBlock"]/div[4]/div/div/div[{}]/div/div[1]/div/a'.format(x))
            name_element = driver.find_element_by_xpath('//*[@id="productCategoryBlock"]/div[4]/div/div/div[{}]/div/div[2]/div[1]/a'.format(x))
            quick_view_link = content.get_attribute('href')
            quick_view_links[name_element.text] = quick_view_link
        except Exception as err:
            print('unable to get link for ornament in hallmark_ornaments_com err {}'.format(err))
    return quick_view_links