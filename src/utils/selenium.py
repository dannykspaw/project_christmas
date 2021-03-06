from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print('Creating selenium driver...')

# setup driver for chrome instance
chrome_options = Options()	
chrome_options.add_argument('--no-sandbox')	
chrome_options.add_argument('--window-size=1920,1080')	
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)