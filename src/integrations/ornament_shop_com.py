from os import path, getpid
import requests
import pandas as pd

from utils.config import config
from utils.selenium import driver
from models import products


integration_name = path.basename(__file__).replace('.py', '')
COLUMNS=products.columns


def get_year_links():
    url = 'https://www.ornament-shop.com/hallmark-ornaments-by-year.html'
    driver.get(url)

    content_blocks = driver.find_elements_by_class_name("navList-item")
    year_links = {}

    for block in content_blocks:
        element = block.find_element_by_tag_name("a")
        year_link = element.get_attribute("href")

        segments = year_link.split('/')
        year = segments[3].split('-')[0]

        year_links[year] = year_link

    return year_links


year_links = get_year_links()


def __get_ornament_links_by_year(url, links={}):
    driver.get(url)
    ornament_blocks = driver.find_elements_by_class_name("card")

    for block in ornament_blocks:
        link_block = block.find_element_by_class_name("card-figure")
        element = link_block.find_element_by_tag_name("a")
        ornament_link = element.get_attribute("href")

        name_block = block.find_element_by_class_name("card-title")
        element = name_block.find_element_by_tag_name("a")
        ornament_name = element.get_attribute("text")

        if ornament_name in links.keys():
            print('duplicate ornament name found: {}'.format(ornament_name))

        links[ornament_name] = ornament_link

    try:
        next_page_block = driver.find_element_by_class_name('pagination-item--next')
        next_page_link = next_page_block.find_element_by_tag_name('a').get_attribute('href')
        
        print('next page link found: {}'.format(next_page_link))
        __get_ornament_links_by_year(next_page_link, links)
    except:
        print('no next page found from url: {}'.format(url))
        return links


def get_ornaments_by_year(year):
    year = str(year)
    year_link = year_links[year]
    products = __get_ornament_links_by_year(year_link)
    ornaments_df = pd.DataFrame(columns=COLUMNS)

    for link in products.values():
        ornament_df = get_ornament_by_url(link)
        ornament_df['release_year'] = year
        ornaments_df = ornaments_df.append(ornament_df, ignore_index=True)

    return ornaments_df


def get_ornament_by_url(link):
    # navigate to the ornament details page
    driver.get(link)

    # define and grab all elements from the ornament details page
    brand_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[4]/a/span')
    sku_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[5]')
    name_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/h1')
    price_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[3]/div/span')
    availability_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[6]')
    # id_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[3]/div[1]/form[1]/input[2]')

    # make sure that there is a column for everything in the schema
    ornament_details = dict.fromkeys(COLUMNS, None)
    ornament_details["sku"] = sku_element.text
    ornament_details["name"] = name_element.text
    ornament_details["price"] = price_element.text
    ornament_details["brand"] = brand_element.text
    ornament_details["availability"] = availability_element.text
    # ornament_details["vendor_id"] = id_element.get_attribute('value')
    ornament_details["vendor"] = integration_name
    ornament_details["link"] = link

    ornament_df = pd.DataFrame(ornament_details, index=[0])
    return ornament_df