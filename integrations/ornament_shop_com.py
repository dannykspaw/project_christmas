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
    "Product Release Year",
    "Product Vendor"
]


def cache_product_details(year, details, cache):
    # cache the product details in csv/pickle format
    # print('caching count {} product details from year {}'.format(len(details), year))

    # create seed file if it doesn't already exist
    file_mode = 'a' if path.exists(cache) else 'x'
    insert_header = False if file_mode == 'a' else True
        
    # append the current year to an already existing csv
    details.to_csv(cache, mode=file_mode, header=insert_header)


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
    # navigate to the ornament details page
    driver.get(link)

    # define and grab all elements from the ornament details page
    brand_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[4]/a/span')
    sku_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[5]')
    name_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/h1')
    price_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[3]/div/span')
    availability_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[2]/div/dl/dd[6]')
    id_element = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div/div[1]/section[3]/div[1]/form[1]/input[2]')

    # make sure that there is a column for everything in the schema
    ornament_details = dict.fromkeys(COLUMNS, None)
    ornament_details["Product Code"] = sku_element.text
    ornament_details["Product Name"]: name_element.text
    ornament_details["Product Price"]: price_element.text
    ornament_details["Product Brand"]: brand_element.text
    ornament_details["Product Availability"]: availability_element.text
    ornament_details["Product Id"]: id_element.get_attribute('value')
    ornament_details["Product Release Year"]: year
    ornament_details["Product Vendor"]: "ornament-shop.com"

    return ornament_details
    

if __name__ == "__main__":
    # setup driver for chrome instance
    chrome_options = Options()	
    chrome_options.add_argument('--no-sandbox')	
    chrome_options.add_argument('--window-size=100,100')	
    chrome_options.add_argument('--headless')	
    # chrome_options.add_argument('--disable-gpu')	
    driver = webdriver.Chrome(options=chrome_options)

    url = 'https://www.ornament-shop.com/'

    # get all links for each year
    # todo: cache the year links between starts
    years = get_year_links(driver)

    # check if the year is being filtered
    filtered_year = getenv('YEAR')
    if filtered_year:
        years = { filtered_year: years[filtered_year] }

    # get the cache file path
    completed_products = []
    cache = getenv('CACHE')
    if path.exists(cache):
        # if it exists, get all product names
        cached_products = pd.read_csv(cache)
        completed_products = cached_products['Product Name'].tolist()
        print('loaded {} cached products'.format(len(completed_products)))

    for year, url in years.items():
        print('getting product links for year {} link {}'.format(year, url))

        # get all the product links for this year
        product_links = {}
        get_ornaments(driver, url, product_links)

        i = 0
        count = len(product_links)
        for product, link in product_links.items():
            i += 1

            # skip if this product has already been cached
            if product in completed_products:
                print('{}/{} {} - skipping duplicate for {} at link {}'.format(i, count, year, product, link))
                continue

            print('{}/{} {} - getting details for {} at link {}'.format(i, count, year, product, link))

            # get the ornament details for this link
            product_details = get_ornament_details(driver, link, year)

            # if the cache directory was provided, cache it
            if cache:
                cache_product_details(year, pd.DataFrame(product_details, index=[0]), cache)