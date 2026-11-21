import os
import tempfile
import time
import pandas as pd
from bs4 import BeautifulSoup

def scrape():

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
        driver.get("https://store.steampowered.com/search/?hwtype=0&maxprice=25&tags=4182&supportedlang=english&specials=1&hidef2p=1&ndl=1")
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
    finally: 
        final_html = driver.page_source #all the html from scrolling via Selenium, then parsed via BeautifulSoup
        driver.quit()

    soup = BeautifulSoup(final_html, "html.parser")
    return soup

def parse():

    targets = soup.find_all('a', class_="search_result_row")
    steamdeals = []
    for target in targets:
        name = target.find('span',class_='title')
        discount = target.find('div',class_='discount_pct')
        finalprice = target.find('div',class_= 'discount_final_price')
        ogprice = target.find('div',class_= 'discount_original_price')
        data = {
            'Name':name.text if name else None,
            'Original Price':ogprice.text if ogprice else None,
            'Discount Price':finalprice.text if finalprice else None,
            'Deal':discount.text if discount else None 
        }
        steamdeals.append(data)


    df = pd.DataFrame(steamdeals)
    df.to_csv('results.csv', index = False)
    print(f"scraped deals from {len(df)} games, succesfully exported to results.csv")

if __name__ == '__main__':
        soup = scrape()
        parse()
