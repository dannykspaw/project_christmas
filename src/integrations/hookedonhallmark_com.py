from os import path, getpid
import re
import requests
import pandas as pd

from utils.selenium import driver
from utils.config import config
from ..models import products


integration_name = path.basename(__file__).replace('.py', '')
COLUMNS=products.columns


def get_year_links():
    url = 'https://www.hookedonhallmark.com/keepsake-hallmark-ornaments-by-year.html'
    driver.get(url)

    content_blocks = driver.find_elements_by_class_name("columns-5")
    year_links = {}

    for content in content_blocks:
        for block in content.find_elements_by_tag_name("li"):
            element = block.find_element_by_tag_name("a")
            year_link = element.get_attribute("href")
            name_span = block.find_element_by_tag_name("span")

            try:
                year_img = name_span.find_element_by_tag_name("img")
                img_alt = year_img.get_attribute("alt")
                segments = img_alt.split(' ')
            except:
                segments = name_span.text.split(' ')

            year = segments[0]
            year_links[year] = year_link

    return year_links


# todo: cache the year links between starts
year_links = get_year_links()


def __get_ornament_links_by_year(url, links={}):
    driver.get(url)
    ornament_blocks = driver.find_elements_by_class_name("product-item")

    # try to find the category button that links to the "view all" page
    if len(ornament_blocks) == 0:
        category_blocks = driver.find_elements_by_class_name('sub-categories')
        reg = re.compile(r'view-all', re.IGNORECASE)

        for block in category_blocks:
            view_all_a = block.find_element_by_tag_name('a')
            view_all_link = view_all_a.get_attribute('href')
            is_valid_link = len(reg.findall(view_all_link)) > 0
            if is_valid_link:
                print('using view all page to get products {}'.format(view_all_link))
                driver.get(view_all_link)
                ornament_blocks = driver.find_elements_by_class_name("product-item")
                break

    for block in ornament_blocks:
        name_block = block.find_element_by_class_name("name")
        ornament_name = name_block.text

        a = name_block.find_element_by_tag_name('a')
        ornament_link = a.get_attribute("href")

        if ornament_name in links.keys():
            print('duplicate ornament name found: {}'.format(ornament_name))

        links[ornament_name] = ornament_link

    try:
        pagination_block = driver.find_element_by_class_name('paging')
        paging_elements = pagination_block.find_elements_by_tag_name('a')

        next_page_link = None
        for a in paging_elements:
            if 'next' in a.text.lower():
                next_page_link = a.get_attribute('href')
                break

        if next_page_link is None:
            return links

        print('next page link found: {}'.format(next_page_link))
        __get_ornament_links_by_year(next_page_link, links)
    except Exception as err:
        print('no next page found from url: {} err {}'.format(url, err))


def get_ornaments_by_year(year):
    year = str(year)
    year_link = year_links[year]
    products = __get_ornament_links_by_year(year_link)
    ornaments_df = pd.DataFrame(columns=COLUMNS)

    for link in products.values():
        ornament_df = get_ornament_by_url(link)
        ornament_df['Product Release Year'] = year
        ornaments_df = ornaments_df.append(ornament_df, ignore_index=True)

    return ornaments_df


def get_ornament_by_url(link):
    # navigate to the ornament details page
    driver.get(link)

    # define and grab all elements from the ornament details page
    brand_element = 'hallmark'
    sku_element = driver.find_element_by_xpath('//*[@id="product_id"]')
    price_element = driver.find_element_by_xpath('//*[@id="price"]')
    availability_element = driver.find_element_by_xpath('//*[@id="availability"]')
    id_element = driver.find_element_by_xpath('//*[@id="add"]/input[1]')
    name_element = driver.find_element_by_xpath('//*[@id="add"]/div[2]/div[2]/div[1]/h1')

    # make sure that there is a column for everything in the schema
    ornament_details = dict.fromkeys(COLUMNS, None)
    ornament_details["sku"] = sku_element.text
    ornament_details["price"] = price_element.text
    ornament_details["brand"] = brand_element
    ornament_details["availability"] = availability_element.text
    ornament_details["name"] = name_element.text
    # ornament_details["Product Id"] = id_element.get_attribute('value')
    ornament_details["vendor"] = integration_name
    ornament_details["link"] = link
    
    ornament_df = pd.DataFrame(ornament_details, index=[0])
    return ornament_df
    

if __name__ == "__main__":
    for year, url in year_links.items():
        print('getting product links for year {} link {}'.format(year, url))

        # get all the product links for this year
        product_links = __get_ornament_links_by_year(url)

        i = 0
        count = len(product_links)
        for product, link in product_links.items():
            i += 1
            print('{}/{} {} - getting details for {} at link {}'.format(i, count, year, product, link))

            # get the ornament details for this link
            product_details = get_ornament_by_url(link)