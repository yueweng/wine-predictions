import numpy as numpy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime


class Wine():
  def __init__(self, url):
        PROXY = "23.23.23.23:3128" # IP:PORT or HOST:PORT

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)

        self.url = url
        self.path = r'/Users/yuewengmak/Desktop/chromedriver'
        self.driver = webdriver.Chrome(executable_path = self.path, options=chrome_options)

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

  def run_sel_lazyloading(self):
    # Get the current number of rows
    current_rows_number = len(self.driver.find_elements_by_class_name('explorerCard__explorerCard--3Q7_0'))
    total_number = int(self.driver.find_elements_by_css_selector('.querySummary__querySummary--39WP2')[0].text.split('Showing ')[1].split('wines')[0])
    print("Total Number: ", total_number)
    while current_rows_number < total_number:
        # Scroll down to make new XHR (request more table rows)
        self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
        try:
            self.driver.set_window_position(0,-1000)
            # Wait until number of rows increased       
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

  def create_df(self, rows):
    all_rows = []

    # Let's store each row as a dictionary 
    empty_row = {
        "title": None, "country": None, "continent": None, "ratings": None, "Number of Ratings": None, "Reviews": None, "Image_URL": None
    }
    print(len(rows))
    for row in rows:
      # vintageTitle__wine--U7t9G 
      print(row)
      break

