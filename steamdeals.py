import os
import tempfile
import time
import pandas as pd
from bs4 import BeautifulSoup


# Create a local 'tmp' directory inside your Home folder if it doesn't exist
os.environ["SE_SKIP_DRIVER_IN_PATH"] = "true" #force geckodriver to skip compatibility
user_home_tmp = os.path.expanduser("~/tmp")
os.makedirs(user_home_tmp, exist_ok=True)
# Force Python and Selenium to use this new location for temporary profiles
os.environ["TMPDIR"] = user_home_tmp
tempfile.tempdir = user_home_tmp
#the actual selenium stuff
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless=new") #remove this if you want to actually see the browser window
driver = webdriver.Firefox(options=options)
a = 3 #timekeeper

try:
    x = driver.get("https://store.steampowered.com/search/?hwtype=0&maxprice=25&tags=4182&supportedlang=english&specials=1&hidef2p=1&ndl=1")
    time.sleep(3)
    previousheight= driver.execute_script('return document.body.scrollHeight')
    
    while True: # this while loop continuously scrolls the dyanmically updating Webpage
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(3)
        newheight =  driver.execute_script('return document.body.scrollHeight')
        a += 3 
        print(f"Exposing Full Webpage... Time Elapsed:{a}s")
        if newheight == previousheight: #continues scrolling until heights are equal upon updating(there's nowhere else to go)
            print("Webpage Exposed: Beginning Scraping")
            break
        previousheight = newheight 
except KeyboardInterrupt:
        print("killing script")

final_html = driver.page_source #all the html from scrolling via Selenium, then parsed via BeautifulSoup
soup = BeautifulSoup(final_html, "html.parser") 

targets = soup.find_all('span',class_='title')
discounts = soup.find_all('div',class_='discount_pct')
finalprice = soup.find_all('div',class_= 'discount_final_price')
ogprice = soup.find_all('div',class_= 'discount_original_price')

name = []
deals = []
discountprice = []
originalprice = []

for target in targets:
    name.append(target.text)
for discount in discounts:
    deals.append(discount.text)
for prices in finalprice:
    discountprice.append(prices.text)
for prices in ogprice:
    originalprice.append(prices.text)
#pass wanted info to 4 separate arrays

data = {
    'Name':name,
    'Original Price':originalprice,
    'Discount Price':discountprice,
    'Deal':deals
}

#some data tiles dont have certain elemnts, so to load unequal arrays, so the dataframe is first loaded as rows, then transposed. pandas autofills uncaught elements as none 

df = pd.DataFrame.from_dict(data, orient='index')
df = df.transpose()
df.to_csv('results.csv', index = False)
print(f"scraped deals from {len(df)} games, succesfully exported to results.csv")

