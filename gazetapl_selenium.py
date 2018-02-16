from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

option = webdriver.ChromeOptions()
option.add_argument(" — incognito")

browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=option)
browser.get("http://wiadomosci.gazeta.pl/wiadomosci/0,0.html#Z_HatNav")

articles = browser.find_elements_by_xpath("//article[@class='article']/header/h2/a")
titles = [x.text for x in articles]
sources = [x.get_attribute('href') for x in articles]
print('titles:')
print(titles, '\n')
print('sources:')
print(sources, '\n')

# browser.close()
