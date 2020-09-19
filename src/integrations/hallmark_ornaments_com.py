from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pandas as pd
import time
from csv import reader
import re

COLUMNS=[
    "Product Code",
    "Product Name",
    "Product Price",
    "Product Brand",
    "Product Availability",
    "Product Id",
    "Product Release Year",
    "Product Vendor",
    "Product Link"
]

ornament_df = pd.DataFrame(columns=COLUMNS)

#Set webdriver options
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

action = ActionChains(driver)

# go to website
driver.get("https://www.hallmarkornaments.com/Hallmark-Ornaments-By-Year_c_200.html")

#pull years
year_content_block = driver.find_elements_by_class_name("subcat")

# get year links
year_links = {}

for year in year_content_block[0:48]:
    year_link = year.get_attribute("href")
    year_num = re.findall(r'\d+', year_link)[0]
    year_links[year_num] = year_link+'?viewall=1'

#get number of products
for year in range(1973,1975):
    try:
        driver.get(year_links[str(year)])
        quantity = driver.find_element_by_class_name('product-count')
        num_of_products = quantity.text[26:]
        print(year)
        quick_view_links = []
    except:
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
        product_release_year = year
        product_vendor = "hallmarkornaments.com"
        product_link = driver.current_url

        product_info={"Product Code":product_code,"Product Name":product_name,"Product Price":product_price,"Product Availability":product_availability,"Product Brand":product_brand,"Product Id":product_id,"Product Release Year":product_release_year,"Product Vendor":product_vendor,"Product Link":product_link}
        ornament_df = ornament_df.append(product_info,ignore_index=True)
        print(ornament_df.shape)
        print(ornament_df.columns)
        print(ornament_df.head(5))

driver.quit()
