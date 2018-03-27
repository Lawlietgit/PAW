# Data science challenge 

# imports

import os, sys, pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
from scipy.stats import skew, kurtosis, lognorm, norm, f_oneway, chi2_contingency
#from scipy.stats.mstats import gmean 
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder

def report_change(df_in, df_out): # function to report the size change of the dataframe before and after
	orow = df_in.shape[0]
	ocol = df_in.shape[1]
	nrow = df_out.shape[0]
	ncol = df_out.shape[1]
	print("Old dataframe size:", orow, "rows", ocol, "columns")
	print("New dataframe size:", nrow, "rows", ncol, "columns")

def report_stats(sr): # function to report the statistical parameters of a data set, takes a pandas.series
	sr_mean = np.mean(sr)
#	sr_gmean = gmean(sr)
	sr_median = np.median(sr)
	sr_std = np.std(sr)
	sr_skew = skew(sr)
	sr_kurtosis = kurtosis(sr)
	name = sr.name
	print("Lanching statistical parameter report routine ---> ")
	print("The mean of the", name, " = ", sr_mean)
#	print("The geometric mean of the", name, " = ", sr_gmean)
	print("The stddev of the", name, " = ", sr_std)
	print("The median of the", name, " = ", sr_median)
	print("The skew of the", name, " = ", sr_skew)
	print("The kurtosis of the", name, " = ", sr_kurtosis)
