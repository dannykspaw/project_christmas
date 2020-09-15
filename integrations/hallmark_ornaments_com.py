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
    "Product Vendor"
]

#Set webdriver options
options = Options()
options.headless = False
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

print(year_links)

product_names = []
product_links = []
product_prices = []
product_codes = []
product_availability = []
product_brand = []
product_data_links =[]

driver.get("https://www.hallmarkornaments.com/1998-Hallmark-Ornaments_c_263.html?viewall=1")

for x in range(271,272):
    ornament = driver.find_element_by_xpath('//*[@id="productCategoryBlock"]/div[4]/div/div/div[272]')
    hover = ActionChains(driver).move_to_element(ornament)
    hover.perform()
    print(ornament.text)
    content = driver.find_element_by_class_name("btnQV hidden-xs hidden-sm hidden-md")
    print(content.get_attribute('innerHTML'))
    content.click()


#
# driver.get("https://www.hallmarkornaments.com/1998-Hallmark-Ornaments_c_263.html")
# # item = driver.find_elements_by_xpath("//*[@id='productCategoryBlock']")
# quick_view_locations = driver.find_elements_by_partial_link_text("/product.asp?")
#
# product_location_data = driver.find_element_by_xpath('/html/head/script[7]')
# print(len(quick_view_locations))
# print(content)
#
# for loc in quick_view_locations:
#     product_link = quick_view_locations.get_attribute('href')
#     print(product_link)


# for link in quick_view_links:
#     driver.get(link)
#     print(link)
#     product_location_data = driver.find_element_by_xpath('/html/head/script[7]')
#     print(product_location_data.get_attribute('innerText'))




# for year in year_links[year]:
#     '''go to link'''
#     driver.get(year_link_list[x])
#     try:
#         view_all_link = driver.find_element_by_class_name("category-viewall")
#         view_all_link.click()
#     except:
#         print("No view all")
#     try:
#         product_location_data = driver.find_element_by_xpath('/html/head/script[7]')

# #
# #     try:
# #         number_of_products = driver.find_element_by_class_name('product-count')
# #         number_of_products = number_of_products.text[26:]
# #         #Working on viewing all products here.text
# #         print("NUMBER OF PRODUCTS: ", number_of_products)
# #         product_name_list = driver.find_elements_by_class_name('name')
# #         for x in product_name_list:
# #             product_names.append(x.text)
# #             product_link_location = driver.find_element_by_partial_link_text(x.text)
# #             product_link = product_link_location.get_attribute("href")
# #             product_links.append(product_link)
# #             # print(x.text, " : ", product_link)
# #         print("product links", len(product_links))
# #         # iter_products_num = int(number_of_products)
# #         # for product in iter_products_num:
# #         #     product_name = driver.find_elements_by_class_name("name")
# #     except:
# #         print("NUMBER OF PRODUCTS: 0")
#
# # product_link_df = pd.DataFrame()
# # product_link_df.insert(0,"Links",product_links)
# # product_link_df.to_csv(path_or_buf="product_links.csv", index=False)
#
# # open file in read mode
# with open('/Users/danielkearney-spaw/Desktop/jcbc/hallmarkornaments_com_link_files/hallmark_ornaments_21.csv', 'r') as read_obj:
#     # pass the file object to reader() to get the reader object
#     csv_reader = reader(read_obj)
#     # Iterate over each row in the csv using reader object
#     header = next(csv_reader)
#     # Check file as empty
#     if header != None:
#         for row in csv_reader:
#             # row variable is a list that represents a row in csv
#             print(row)
#             product_url = row[0]
#             product_data_links.append(product_url)
#             driver.get(product_url)
#             try:
#                 price = driver.find_element_by_id("price").text
#                 product_prices.append(price)
#                 code = driver.find_element_by_id("product_id").text
#                 product_codes.append(code)
#                 # print("Appended code and price for ",x)
#                 availability_list = driver.find_elements_by_id("availability")
#                 brand = availability_list[0].text
#                 product_brand.append(brand)
#                 availability = availability_list[1].text
#                 product_availability.append(availability)
#                 name = driver.find_element_by_class_name("page_headers")
#                 product_names.append(name.text)
#             except:
#                 price = "price error"
#                 brand = "brand error"
#                 code = "code error"
#                 availability = "availbility error"
#                 product_prices.append(price)
#                 product_codes.append(code)
#                 product_brand.append(brand)
#                 product_availability.append(availability)
#
# ornament_df = pd.DataFrame()
# ornament_df.insert(0,"Product Code",product_codes)
# ornament_df.insert(1,"Product Name",product_names)
# ornament_df.insert(2,"Product Price",product_prices)
# ornament_df.insert(3,"Product Brand", product_brand)
# ornament_df.insert(4,"Product Availability", product_availability)
# ornament_df.insert(5,"Product Link",product_data_links)
# ornament_df.to_csv(path_or_buf="/Users/danielkearney-spaw/Desktop/jcbc/hallmarkornaments_com_prod_info/hallmark_ornaments_21_prod_info.csv", index=False)
#
# print("DONE")
# driver.quit()
