from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# setup driver for chrome instance
chrome_options = Options()	
chrome_options.add_argument('--no-sandbox')	
chrome_options.add_argument('--window-size=100,100')	
chrome_options.add_argument('--headless')	
# chrome_options.add_argument('--disable-gpu')	
driver = webdriver.Chrome(options=chrome_options)