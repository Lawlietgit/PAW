# Data science challenge C1 - Qi Li
# Program driver 

# imports and link to other modules
from standard_import import *
from data_cleaning import *
from feature_engineering import *
from dist_distribution import *
from speed_distribution import *
from model import *

tic = pd.Timestamp.now()

if len(sys.argv) < 3:
	print("@@@@@@@@@@@@@@@@@@@@@@ERROR!@@@@@@@@@@@@@@@@@@@@@@")
	print("Wrong number of arguments! Run the program as follows:")
	print("python driver.py [is_remove_old_data] (Y/n) [is_gen_plots] (Y/n)")
	print("[is_remove_old_data]: Y/n, if Y, remove the old .csv file and re-download")
	print("[is_gen_plots]	   : Y/n, if Y, generate all the plots (could be time consuming ...)")
	print("@@@@@@@@@@@@@@@@@@@@@@ERROR!@@@@@@@@@@@@@@@@@@@@@@")
	sys.exit()

def str2bool(v): # str to bool
  return v.lower() in ("yes", "true", "y", "1")

# Important variables
is_remove_old_data = str2bool(sys.argv[1]) # if "True", remove the old copy of the data and re-download
is_gen_plots 	   = str2bool(sys.argv[2]) # if "True", general all plots (could be time consuming ...)
min_tspan		   = 30.0		 # lower bound of trip time span for data cleaning, 30 seconds
max_tspan		   = 36000.0	 # upper bound of trip time span, 10 hours
min_dist		   = 0.1		 # lower bound of trip distance for data cleaning, 0.1 mile
max_dist		   = 20.0	 	 # upper bound of trip distance, 20 miles
min_speed		   = 3.1		 # lower bound of average trip speed for data cleaning, 3.1 mph (human walking speed)
max_speed		   = 40.0	 	 # upper bound of average trip speed, 40 mph
anova_sample_size  = 1000		 # sample size for the anova test
sample_size		   = 10000		 # sample size for the predictive model		
n_fold			   = 10			 # number of folds for the cross-validation

# Download the data, read into a pandas dataframe and report the number of rows and columns

print("\n****************************BEGINNING OF DRIVER EXECUTION*****************************")
print("Analysis of NYC green taxi data in September, 2015 \n")
print("Data science challenge - Qi Li")
print("**********************************************************************************\n")

url = 'https://s3.amazonaws.com/nyc-tlc/trip+data/green_tripdata_2015-09.csv'

if os.path.exists('green_tripdata_2015-09.csv'): # if .csv already exists
	if is_remove_old_data: # if remove the old copy
		os.remove('green_tripdata_2015-09.csv') # remove the old copy
		print("Downloading data from", url, "...") # download a new copy
		df_in = pd.read_csv(url)
	else:
		df_in = pd.read_csv('green_tripdata_2015-09.csv') # read in the current copy
else: # download the .csv if it doesn't exist
    print("Downloading data from", url, "...")
    df_in = pd.read_csv(url)

print("\nReporting the size of the original data:")
print("Total number of rows: ", df_in.shape[0]) # print the total number of rows
print("Total number of cols: ", df_in.shape[1], "\n") # print the total number of cols

# Perform preliminary data cleaning process, store the result into df_raw
df_raw = clean_data(df_in) 

# Perform feature engineering and further data cleaning precoess, store the result into df 
df = fe_data(df_raw, is_gen_plots, min_tspan, max_tspan, min_dist, max_dist, min_speed, max_speed)	

'''
# save the data to pickle, not needed for the submission
df_raw.to_pickle('dataset_cl.pkl') 
df.to_pickle('dataset.pkl')
'''

# Perform trip distance analysis
dist_analysis(df_raw, df, is_gen_plots, max_dist)

# Perform average trip speed analysis
speed_analysis(df, is_gen_plots, anova_sample_size)

# Construct the predictive model and report the results
run_models(df, is_gen_plots, sample_size, n_fold)

toc = pd.Timestamp.now()

print("Total execution time: ", (toc-tic).seconds, "seconds!\n")
print("****************************END OF DRIVER EXECUTION*****************************")
