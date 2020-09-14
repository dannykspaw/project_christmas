from os import getenv, path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd


COLUMNS=[
    "Product Code",
    "Product Name",
    "Product Price",
    "Product Brand",
    "Product Availability",
    "Product Id",
    "Product Release Year"
]


def cache_product_details(year, links, cache):
    # cache the product links in csv/pickle format
    print('caching count {} product links from year {}'.format(len(links), year))

    # create seed file if it doesn't already exist
    if not path.exists(cache):
        open(cache, "x")

    # append the current year to an already existing csv
    links.to_csv(cache, mode='a', header=False)


def get_year_links(driver):
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


def get_ornaments(driver, url, links={}):
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
        get_ornaments(driver, next_page_link, links)
    except:
        print('no next page found from url: {}'.format(url))


def get_ornament_details(driver, link, year):
    driver.get(link)

    brand_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[4]/a/span')
    sku_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[5]')
    name_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/h1')
    price_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[3]/div/span')
    availability_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[6]')
    id_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[3]/div[1]/form[1]/input[2]')

    ornament_details = {
        "Product Code": sku_element.text,
        "Product Name": name_element.text,
        "Product Price": price_element.text,
        "Product Brand": brand_element.text,
        "Product Availability": availability_element.text,
        "Product Id": id_element.get_attribute('value'),
        "Product Release Year": year
    } 

    return ornament_details
    

chrome_options = Options()	
chrome_options.add_argument('--no-sandbox')	
chrome_options.add_argument('--window-size=100,100')	
chrome_options.add_argument('--headless')	
# chrome_options.add_argument('--disable-gpu')	
driver = webdriver.Chrome(options=chrome_options)

url = 'https://www.ornament-shop.com/'

years = get_year_links(driver)

for year, url in years.items():
    print('getting product links for year {} link {}'.format(year, url))

    # get all the product links for this year
    product_links = {}
    get_ornaments(driver, url, product_links)

    product_details_df = pd.DataFrame(columns=COLUMNS)

    i = 0
    count = len(product_links)
    for product, link in product_links.items():
        print('{}/{} {} - getting details for {} at link {}'.format(i, count, year, product, link))

        product_details = get_ornament_details(driver, link, year)
        product_details_df = product_details_df.append(product_details, ignore_index=True)

        i += 1

    cache = getenv('CACHE')
    if cache:
        cache_product_details(year, product_details_df, cache)