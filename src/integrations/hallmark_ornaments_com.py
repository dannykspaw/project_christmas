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
COLUMNS=products.columns

action = ActionChains(driver)

# go to website
driver.get("https://www.hallmarkornaments.com/Hallmark-Ornaments-By-Year_c_200.html")

#pull years
year_content_block = driver.find_elements_by_class_name("subcat")

year_links = {}

for year in year_content_block[0:48]:
    year_link = year.get_attribute("href")
    year_num = re.findall(r'\d+', year_link)[0]
    year_links[year_num] = year_link+'?viewall=1'

def get_ornament_by_url(link):
    single_product_df = pd.DataFrame(columns=COLUMNS)
    driver.get(link)

    product_info = {}

    #find javascript variable containing product details
    product_location_data = driver.find_element_by_xpath('/html/head/script[7]')
    sku_info_blob = product_location_data.get_attribute('innerText')
    sku_info = sku_info_blob.replace('"','').replace("' '",'').replace("{",'').replace("var _3d_item =",'').replace("}",'').split('",')

    #prepare javascript var item variable for parsing
    sku_price_split = sku_info[0].split(",price")[1]
    sku_name_code_split = sku_info[0].split(",price")[0]

    # parse into product details
    product_code = sku_name_code_split.split(",id:")[1].split(",name")[0]
    product_name = sku_name_code_split.split("name:")[1]
    product_price = sku_price_split.split(":")[1].split(",availability")[0]
    product_availability = sku_price_split.split("availability:")[1].split(",currency")[0].replace("0","Not In Stock").replace("1","In Stock")
    product_brand = "Hallmark"
    product_id = sku_name_code_split.split("catalogid:")[1].split(",id")[0]
    product_vendor = integration_name
    product_link = driver.current_url
    product_info={"sku":product_code,"name":product_name,"price":product_price,"availability":product_availability,"brand":product_brand,"vendor":product_vendor,"link":product_link}
    single_product_df = single_product_df.append(product_info,ignore_index=True,sort=True)
    return single_product_df

# get year links

def get_ornaments_by_year(year):
    ornaments_df = pd.DataFrame(columns=COLUMNS)
    try:
        driver.get(year_links[str(year)])
        quantity = driver.find_element_by_class_name('product-count')
        num_of_products = quantity.text[26:]
        print(year)
        quick_view_links = []
    except Exception as e:
        print(e)
        year += 1
    #create quick view links within year
    for x in range(1,int(num_of_products)+1):
        try:
            ornament = driver.find_element_by_xpath('//*[@id="productCategoryBlock"]/div[4]/div/div/div[{}]'.format(str(x)))
            hover = ActionChains(driver).move_to_element(ornament)
            hover.perform()
            content = driver.find_element_by_xpath('//*[@id="productCategoryBlock"]/div[4]/div/div/div[{}]/div/div[1]/div/a'.format(x))
            quick_view_link = content.get_attribute('href')
            quick_view_links.append(quick_view_link)
        except:
            print("nada")
    #pull product data from quick view link
    for link in quick_view_links:
        #run function for single link and return single link df
        single_product_df = get_ornament_by_url(link)
        single_product_df['release_year'] = year
        ornaments_df = ornaments_df.append(single_product_df,ignore_index=True,sort=True)
    return ornaments_df

#get number of products
