import numpy as numpy
import pandas as pd
import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt

class Wine():
  def __init__(self):
      self.collection = None
      self.df = None

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
    return self

  def representsInt(self, s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

  def plot_type_based_on_popularity(self):
    ratings_wine = self.df.groupby('type').agg({'num_ratings': 'count'}).reset_index()
    ratings_wine.sort_values(by=['num_ratings'], ascending=False, inplace=True)
    fig, ax = plt.subplots(figsize=[20, 10])
    ax.bar(ratings_wine['type'], ratings_wine['num_ratings'])
    ax.set_title('Wine Types based on Popularity', fontsize=20, pad=20)
    ax.set_xlabel('Wine Types', fontsize=20)
    ax.set_ylabel('Num of Ratings', fontsize=20)
    plt.savefig('images/wine_types_popularity.png')

  def plot_country_based_on_type_popularity(self, ty):
    wine_df = self.df
    type_df = wine_df[wine_df['type'] == ty]
    type_df = type_df.groupby('country').agg({'num_ratings': 'count'}).reset_index()
    type_df.sort_values(by='num_ratings', ascending=False, inplace=True)
    
    fig, ax = plt.subplots(figsize=[20, 10])
    ax.bar(type_df['country'], type_df['num_ratings'])
    ax.set_xlabel('Country', fontsize=20)
    ax.set_ylabel('Num of Ratings', fontsize=20) 
    ax.set_title('{} Wine Based on Popularity'.format(ty), fontsize=20, pad=20)
    plt.savefig('images/{}_country_types_popularity.png'.format(ty.lower()))

  def country_rating_plot(self):
    types_wine = ['Sparkling', 'Red', 'White', 'Rosé', 'Dessert', 'Port']

    for ty in types_wine:
      self.plot_country_based_on_type_popularity(ty)
