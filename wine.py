import numpy as numpy
import pandas as pd
import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

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

  def get_df_group_by_type(self):
    type_df = self.df.groupby(['type']).agg({'ratings': 'mean', 'num_ratings': 'sum', 'price': 'mean'}).reset_index()
    type_df.sort_values(by=['price'], ascending=False)

    return type_df

  def plot_num_ratings_price(self, type_df):
    wine_df = self.df
    unique_type = type_df['type'].unique()
    color = ['brown', 'green', 'red', 'yellow', 'blue', 'purple']
    fig, ax = plt.subplots(figsize=[20,10])

    for idx, ty in enumerate(unique_type):
        uniq_type_df = wine_df[wine_df['type'] == ty]
        ax.scatter(uniq_type_df['num_ratings'], uniq_type_df['price'], label=ty, color=color[idx])
    plt.legend(fontsize=20)

    ax.set_title('Num Ratings vs Price', fontsize=20, pad=20)
    ax.set_xlabel('Num Ratings', fontsize=20)
    ax.set_ylabel('Price', fontsize=20)

    # plt.savefig('images/num_ratings_price.png', bbox_inches = "tight")
  
  def get_dummies(self, col):
    wine_df = self.df
    self.dummies = pd.get_dummies(wine_df[col])
    return self

  def combine_dummies(self, *args):
    shorten_df = self.df.drop(columns=['location', 'region', 'image_url', 'reviews'])
    for dummy in args:
      shorten_df = pd.concat([shorten_df, dummy], axis=1)

    return shorten_df

  def get_train_data(self, final_dummy):
    train_data = final_dummy[(final_dummy['price'] > 0.0) & (final_dummy['vintage'] > 0.0)]
    X = train_data.drop(columns=['price', 'type', 'grapes', 'id', 'title', 'country'])
    y = train_data['price']

    return X, y

  def split_data(self, X, y, test_size=0.33):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    return X_train, X_test, y_train, y_test
