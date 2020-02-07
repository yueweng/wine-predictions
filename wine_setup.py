import numpy as numpy
import pandas as pd
import time
import copy
import pymongo
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

class WineSetup():
  def __init__(self, url):
        self.url = url
        self.path = r'/Users/yuewengmak/Desktop/chromedriver'
        self.driver = webdriver.Chrome(executable_path = self.path)

  def setup_driver(self):

    self.driver.implicitly_wait(30)
    self.driver.get(self.url)

  def tracking(self):
    self.run_timestamp()
    self.run_sel_lazyloading()
    self.run_timestamp()

  def run_timestamp(self):
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    
    print('Current Timestamp: ', timestampStr)

  def run_sel_lazyloading(self, split, sleep=10):
    # Get the current number of rows
    current_rows_number = len(self.driver.find_elements_by_class_name('explorerCard__explorerCard--3Q7_0'))
    total_number = int(self.driver.find_elements_by_css_selector('.querySummary__querySummary--39WP2')[0].text.split('Showing ')[1].split(split)[0])
    print("Total Number: ", total_number)
    while current_rows_number < total_number:
        # Scroll down to make new XHR (request more table rows)
        self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
        try:
            self.driver.set_window_position(0,-1000)
            # Wait until number of rows increased
            time.sleep(sleep)    
            wait(self.driver, 50).until(lambda drive: len(self.driver.find_elements_by_class_name('explorerCard__explorerCard--3Q7_0')) > current_rows_number)
            # Update variable with current rows number
            current_rows_number = len(self.driver.find_elements_by_class_name('explorerCard__explorerCard--3Q7_0'))
            if current_rows_number % 200 == 0:
              print("Curr Row Number: ", current_rows_number)
        # If number of rows remains the same after 5 seconds passed, break the loop
        # as there no more rows to receive
        except TimeoutException:
            break

  def create_rows(self):
    html = BeautifulSoup(self.driver.page_source, 'lxml')
    div = html.find("div", {"class": "explorerPage__results--3wqLw"})
    rows = html.find_all("div", {"class": "explorerCard__explorerCard--3Q7_0"})
    
    return rows

  def store_list(self, rows, type):
    all_rows = []

    # Let's store each row as a dictionary 
    empty_row = {
        "title": None, "location": None, "country": None, "price": 0.0, "type": None, "ratings": None, "num_ratings": None, "reviews": None, "url": None, "vintage": ""
    }

    for row in rows:
        new_row = copy.copy(empty_row)
        # A list of all the entries in the row.
        new_row['title'] = row.find("span", {"class": "vintageTitle__wine--U7t9G"}).text
        location = row.find("div", {"class": "vintageLocation__vintageLocation--1DF0p"})
        new_row['location'] = location.findChildren()[-1].text
        country = row.find("i", {"class": "vintageLocation__countryFlag--1HbXr"})['title']
        new_row['country'] = country
        price_button = row.find("button", {"class": "addToCartButton__addToCartButton--qZv9F"})
        if price_button:
            new_row['price'] = (float(price_button.find("span").text.replace("$", "")))
        new_row['type'] = type
        new_row['ratings'] = row.find("div", {"class": "vivinoRatingWide__averageValue--1zL_5"}).text
        new_row['num_ratings'] = int(row.find("div", {"class": "vivinoRatingWide__basedOn--s6y0t"}).text.split()[0])
        review_div = row.find("div", {"class": "review__note--2b2DB"})
        if review_div:
            new_row['reviews'] = review_div.text
        clean_div = row.find("div", {"class": "cleanWineCard__cleanWineCard--tzKxV cleanWineCard__row--CBPRR"})
        if clean_div:
            new_row['url'] = 'https://www.vivino.com' + clean_div.find("a")['href']
        all_rows.append(new_row)

    return all_rows

  def connect_mongo(self, all_rows):
    client = MongoClient('localhost', 27017)
    wine_db = client['wine']
    types = wine_db['types']

    for row in all_rows:
      types.insert_one(row)
