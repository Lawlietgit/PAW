# Data science challenge C1 - Qi Li
# Data cleaning module 

from standard_import import *

def clean_data(df_in): 
	'''
	Data cleaning for the dataset:
	0. Remove the white spaces in the column names
	1. Drop the whole 'Ehail_fee' column
	2. Filling the missing values in 'Trip_type' column with 1.0
	3. Change the dtype of the datetime columns 
	3. Take the absolute value of the price related columns
	4. Drop all rows with a 'Total_amount' < 2.50
	5. Check if the pieces of the prices add up to the total and drop the mismatching rows 
	6. Remove the rows with invalid 'Extra' column
	7. Clean up the Passenger_count column, replace the zeroes by the most frequent value (1)
	8. Clean up the columns with categorial data
	'''
	print("=====================================================================================")
	print("Data Cleaning Routine Launched -------->   ")
	print("-------------------------------------------------------------------------------------\n")

	df_out = df_in.copy() # make a new copy of the dataframe to avoid some "Warnings" when changing the dataframe

	df_out.rename(columns = lambda x: x.strip(), inplace = True) # remove the white spaces in the column names

	# check the number of missing values for each column:
	print("Checking the number of missing values in each column:")
	print(pd.isnull(df_out).sum()) 

	print("\nDropping the \'Ehail_fee\' column ... \n")
	df_out.drop(['Ehail_fee'], axis = 1, inplace = True) # drop the whole 'Ehail_fee' column

	# check the percentage of the one-way trips:
	print("Percentage of \'Trip_type\' = 1.0:")
	print((df_out['Trip_type'] == 1).sum()/df_out.shape[0]*100, "%")
	print("Filling the missing values for \'Trip_type\' with 1.0 ... \n")
	df_out['Trip_type'].fillna(1.0, inplace = True)

	# convert to datetime and create new columns for year, month, day, hour, minute, second
	print("Converting the datetime object columns to datetime type ...")
	df_out['lpep_pickup_datetime'] = pd.to_datetime(df_out['lpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
	df_out['Lpep_dropoff_datetime'] = pd.to_datetime(df_out['Lpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')

	# define all the columns related to the price, which should only contain positive float numbers
	price_cols = ['Fare_amount', 'MTA_tax', 'Extra',
				  'Tip_amount', 'Tolls_amount', 
				  'improvement_surcharge', 'Total_amount'] # price related columns
	print("\nTaking the absolute value of the \'price\' related columns ... \n")
	df_out[price_cols] = df_out[price_cols].apply(lambda x: np.abs(x), axis = 0)

	# print out the percentage of rows with total fare less than 2.50
	print("Percentage of rows with total fare < 2.50:")
	print(df_out['Total_amount'][df_out['Total_amount'] < 2.50].shape[0]/df_out.shape[0]*100, "%")
	print("Dropping the rows with total fare < 2.50 ... \n")
	df_out = df_out[df_out['Total_amount'] >= 2.50] # dropping the rows with total_fare < 2.50

	print("Calculating the difference between the total fare and the sum of the pieces for each row and store in a new column ...")
	df_out['Delta_amount'] = np.abs(df_out['Fare_amount'] + df_out['Extra'] + df_out['MTA_tax'] 
						+ df_out['Tip_amount'] + df_out['Tolls_amount'] + df_out['improvement_surcharge'] 
						- df_out['Total_amount']) # calculated the difference and store in a new column
	# print out the percentage of rows with mismatching total fare 
	print("Percentage of rows with mismatching total fare:")
	print(df_out['Delta_amount'][df_out['Delta_amount'] >= 1e-5].shape[0]/df_out.shape[0]*100, "%")
	print("Dropping the rows with wrong total fare ... \n")
	df_out = df_out[df_out['Delta_amount'] < 1e-5] # dropping the rows with mismatching total_fare
	df_out.drop(['Delta_amount'], axis = 1, inplace = True) # drop the whole 'Delta_amount' column since it is only used for checking purpose
	
	# check the 'Extra' column
	print("Checking the \'Extra\' column:")
	print(df_out['Extra'].value_counts())
	print("Dropping the rows with wrong \'Extra\' column ... \n")
	df_out = df_out[(df_out['Extra'] == 0.0) | (df_out['Extra'] == 0.5) | (df_out['Extra'] == 1.0)] # dropping the rows with wrong 'Extra' value

	# check the 'Passenger_count' column
	print("Checking the \'Passenger_count\' column:")
	print(df_out['Passenger_count'].value_counts())
	print("Replacing the rows with 0 \'Passenger_count\' with the most frequent value (1) ... \n")
	df_out.loc[df_out['Passenger_count'] == 0, 'Passenger_count'] = 1 # replacing the 0 Passenger_count by 1
	'''
	# check the 'longitude' and 'latitude' columns
	print("Replacing the invalid longitudes and latitudes with NaN ... ")
	# replacing the invalid longtitudes and latidudes with NaN
	df_out['Pickup_longitude'] = df_out['Pickup_longitude'].apply(lambda x: np.nan if (x < -74.5) or (x > -73.2) else x)
	df_out['Dropoff_longitude'] = df_out['Dropoff_longitude'].apply(lambda x: np.nan if (x < -74.5) or (x > -73.2) else x)
	df_out['Pickup_latitude'] = df_out['Pickup_latitude'].apply(lambda x: np.nan if (x < 40.3) or (x > 41.0) else x)
	df_out['Dropoff_latitude'] = df_out['Dropoff_latitude'].apply(lambda x: np.nan if (x < 40.3) or (x > 41.0) else x)
	print("Mean pick-up coordinate:")
	print(np.mean(df_out['Pickup_longitude']),np.mean(df_out['Pickup_latitude']))
	print("Mean drop-off coordinate:")
	print(np.mean(df_out['Dropoff_longitude']),np.mean(df_out['Dropoff_latitude']))
	long_lati_cols = ['Pickup_longitude', 'Pickup_latitude',
					  'Dropoff_longitude', 'Dropoff_latitude'] # columns related to longtitude and latitude
	print("Replacing the NaN's in longitudes and latitudes with np.mean() ... \n")
	df_out[long_lati_cols] = df_out[long_lati_cols].fillna(np.mean(df_out[long_lati_cols]))
	'''
	# check the columns with categorial values:
	df_out.loc[df_out['Store_and_fwd_flag'] == 'Y', 'Store_and_fwd_flag'] = 1
	df_out.loc[df_out['Store_and_fwd_flag'] == 'N', 'Store_and_fwd_flag'] = 0
	df_out['Store_and_fwd_flag'].astype('int64', inplace = True)
	df_out.loc[df_out['RateCodeID'] == 99, 'RateCodeID'] = 1

	print("-------------------------------------------------------------------------------------")
	print("Data Cleaning Routine Finished :-) ")
	report_change(df_in,df_out)
	print("=====================================================================================\n")

	return df_out
