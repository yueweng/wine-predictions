import numpy as numpy
import pandas as pd
import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt

class Wine():
  def __init__(self):
      self.collection = None
      self.df = None
      self.dummies = None

  def get_wine_data(self):
    client = MongoClient('localhost', 27017)
    wine_db = client['wine']
    self.collection = wine_db['types']

    return self

  def create_df(self):
    '''{'_id': ObjectId('5e34c6e0ac2e8d38fb91773e'), 'title': 'J. Schram Brut 2008', 
    'location': 'North Coast', 'region': 'California', 'country': 'United States', 'price': 99.0, 
    'type': 'Sparkling', 'ratings': '4.5', 'num_ratings': 191, 'reviews': None, 
    'image_url': 'images.vivino.com/thumbs/4NLjpfRDSeaCN147hSePKA_pb_x300.png'}'''
    lst = []
    for row in self.collection.find():
      if 'review' in row:
        reviews = row['review']
      else:
        reviews = None
      dict_row = {'id': row['_id'], 'title': row['title'], \
                  'location': row['location'], 'region': row['region'], \
                  'country': row['country'], 'price': row['price'], \
                  'type': row['type'], 'ratings': float(row['ratings']), 'num_ratings': row['num_ratings'], \
                  'reviews': reviews, 'image_url': row['image_url']}

      lst.append(dict_row)
    
    self.df = pd.DataFrame(lst)
    return self

  def create_vintage_column(self):
    self.df['vintage'] = self.df['title'].apply(lambda x: int(x.split(' ')[-1]) if self.representsInt(x.split(' ')[-1]) else None)
    return self.df

  def create_grape_column(self):
    self.df['grapes'] = None

    grapes = ['Chardonnay', 'Riesling', 'Malbec', 'Pinot Noir', 'Merlot', 'Sauvignon Blanc', 'Cabernet Sauvignon', 'Shiraz', 'Syrah']

    for idx, row in self.df.iterrows():
        for g in grapes:
            if g in row['title']:
                self.df.loc[idx, 'grapes'] = g
    return self.df

  def fill_null_value(self, col):
    self.df[col].fillna(0, inplace=True)

  def representsInt(self, s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

  def plot_graph(self, x, y, title, xlabel, ylabel, image_url, fontsize=20, pad=20):
    fig, ax = plt.subplots(figsize=[20, 10])
    ax.bar(x, y)
    ax.set_title(title, fontsize=fontsize, pad=pad)
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    plt.savefig(image_url)

  def plot_type_based_on_popularity(self):
    ratings_wine = self.df.groupby('type').agg({'num_ratings': 'count', 'price': 'mean'}).reset_index()
    ratings_wine.sort_values(by=['num_ratings'], ascending=False, inplace=True)
    self.plot_graph(ratings_wine['type'], ratings_wine['num_ratings'], 'Wine Types based on Popularity', 'Wine Types', 'Num of Ratings', 'images/wine_types_popularity.png')

    ratings_wine.sort_values(by='price', ascending=False, inplace=True)
    self.plot_graph(ratings_wine['type'], ratings_wine['price'], 'Wine Types based on Price', 'Wine Types', 'Price', 'images/wine_types_price.png')

    # fig, ax = plt.subplots(figsize=[20, 10])
    # ax.scatter(ratings_wine['num_ratings'], ratings_wine['price'])


  def plot_country_based_on_type_popularity(self, ty):
    wine_df = self.df
    type_df = wine_df[wine_df['type'] == ty]
    type_df = type_df.groupby('country').agg({'num_ratings': 'count', 'price': 'mean'}).reset_index()
    type_df.sort_values(by='num_ratings', ascending=False, inplace=True)

    self.plot_graph(type_df['country'], type_df['num_ratings'], '{} Wine Based on Popularity'.format(ty), 'Country', 'Num of Ratings', 'images/{}_country_types_popularity.png'.format(ty.lower()))

    type_df.sort_values(by='price', ascending=False, inplace=True)
    self.plot_graph(type_df['country'], type_df['price'], '{} Wine Based on Price'.format(ty), 'Country', 'Price', 'images/{}_country_types_price.png'.format(ty.lower()))

  def country_rating_plot(self):
    types_wine = ['Sparkling', 'Red', 'White', 'Rosé', 'Dessert', 'Port']

    for ty in types_wine:
      self.plot_country_based_on_type_popularity(ty)

  def get_us_wines(self):
    us_df = self.df[self.df['country'] == 'United States']
    return us_df

  def plot_us_type_wine(self, us_df):
    us_type = us_df.groupby('type').agg({'num_ratings': 'sum', 'ratings': 'mean'}).reset_index()
    us_type.sort_values(by=['num_ratings'], ascending=False, inplace=True)

    self.plot_graph(us_type['type'], us_type['num_ratings'], 'Wine Types based in United States', 'Type', 'Num of Ratings', 'images/wine_types_us.png')

  def plot_red_white_us_wine(self, us_df):
    types = ['Red', 'White']

    for t in types:
      color_us_df = us_df[us_df['type'] == t]
      color_type = color_us_df.groupby('grapes').agg({'num_ratings': 'sum'}).reset_index()
      color_type.sort_values(by=['num_ratings'], ascending=False, inplace=True)

      self.plot_graph(color_type['grapes'], color_type['num_ratings'], '{} Wine based on Grapes in the United States'.format(t), 'Grapes', 'Num Ratings', 'images/{}_wine_grapes_us.png')
  
  def get_dummies(self, col):
    wine_df = self.df
    self.dummies = pd.get_dummies(wine_df[col])
    return self

  def combine_dummies(self, *args):
    shorten_df = self.df.drop(columns=['location', 'region', 'image_url', 'reviews'])
    for dummy in args:
      shorten_df = pd.concat([shorten_df, dummy], axis=1)

    return shorten_df
