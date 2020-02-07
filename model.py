import numpy as np
import pandas as pd
import statsmodels.api as sm
import scipy.stats as scs

import matplotlib
import matplotlib.pyplot as plt

class Model():
  def __init__(self):
      pass

  def calculate_rmse(self, y_test, y_pred):
    count = 0

    for idx, ele in enumerate(y_test):
        count += (ele - y_pred[idx])**2

    return (count/len(y_test))**(1/2)