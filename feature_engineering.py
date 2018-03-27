# Data science challenge C1 - Qi Li
# Feature engineering module 

from standard_import import *

def fe_data(df_in, is_gen_plots, min_tspan, max_tspan, min_dist, max_dist, min_speed, max_speed): 
	'''
	Feature Engineering for the dataset:
	0. Inputs: df_in 				 -- input, 						   pandas.dataframe 
			   is_gen_plots 		 -- if True, generate plots, 	   bool
			   min and max time_span -- limits of filtering time_span, float64 
			   min and max distance  -- limits of filtering distance,  float64
			   min and max speed     -- limits of filtering speed,     float64
	1. Adding new column 'Week'
	2. Adding new column 'Day_of_month'
	3. Adding new column 'Day_of_week'
	4. Adding new column 'Hour' 
	5. Calculate the time span for each trip and store it in a new column 'Speed'
	6. Perform further data cleaning to filter out outliners of 'Speed', 'Trip_distance', and 'Time_span'
	7. Calculate the fare per mile (in dollars/mile) and store it in a new column 'Fare_per_mile'
	8. Perform further data cleaning to filter out outliners of 'Fare_per_mile'
	'''
	print("=====================================================================================")
	print("Feature Engineering Routine Launched -------->   ")
	print("-------------------------------------------------------------------------------------\n")

	df_out = df_in.copy() # make a new copy of the dataframe to avoid some "Warnings" when changing the dataframe

	# Adding 4 new columns to describe the time and calculate the time span
	print("Adding two new columns \'Day_of_week\' and \'Day_of_month\' ...")
	print("Calculating the time span for each trip and store it in a new column \'Time_span\' ...")
	df_out['Week'] = df_out['lpep_pickup_datetime'].dt.week - 35 # create a new column for the week of September, 09/01/2015 is the 36th week
	df_out['Hour'] = df_out['lpep_pickup_datetime'].dt.hour # create a new columns for the hour of the day of the taxi rides
	df_out['Day_of_week'] = df_out['lpep_pickup_datetime'].dt.dayofweek # create a new columns for the day of week of the taxi rides
	df_out['Day_of_month'] = df_out['lpep_pickup_datetime'].dt.day # create a new columns for the day of month of the taxi rides
	df_out['Time_span'] = (df_out['Lpep_dropoff_datetime'] - df_out['lpep_pickup_datetime']).dt.seconds # calculating the time span and store

	# Adding a new column 'Speed' and perform further data cleaning
	print("\nAdding a new column \'Speed\' ...")
	print("Dropping rows with outliners in \'Trip_distance\'/\'Speed\'/\'Time_span\'...")
	df_out = df_out[(df_out['Time_span'] > min_tspan) & (df_out['Time_span'] < max_tspan)] # filter out trip with average speed > 40 mph or < 1 mph
	df_out['Speed'] = df_out['Trip_distance']/df_out['Time_span']*3600.0 # create a new column for the average speed, in mph
	df_out = df_out[(df_out['Speed'] < max_speed) & (df_out['Speed'] > min_speed)] # filter out trip with average speed > 40 mph or < 1 mph
	df_out = df_out[(df_out['Trip_distance'] > min_dist) & (df_out['Trip_distance'] < max_dist)] # filter out trip shorter than 0.1 mile or longer than 20 miles
	print("Average speed mean is", np.mean(df_out['Speed']), "mph")
	print("Average speed median is", np.median(df_out['Speed']), "mph")
	
	# Adding a new column 'Fare_per_mile' and perform further data cleaning
	print("\nAdding a new column \'Fare_per_mile\' ...")
	print("Dropping rows with outliners in \'Fare_per_mile\'...")
	df_out['Fare_per_mile'] = df_out['Total_amount']/df_out['Trip_distance'] # create a new column for the fare/mile, in $/mile
	df_out = df_out[(df_out['Fare_per_mile'] < 20.0) & (df_out['Fare_per_mile'] > 2.5)] # filter out trip with fare/mile > 20.0 or < 2.5 
	print("Fare/mile mean is", np.mean(df_out['Fare_per_mile']), "$/mile")
	print("Fare/mile median is", np.median(df_out['Fare_per_mile']), "$/mile")

	if is_gen_plots:
		print("\nPrinting the histogram plot for \'Fare_per_mile\', saving to \'fpm.png\' ...")	
		fig2, ax = plt.subplots(1,1,figsize=(6, 6))
		df_out['Fare_per_mile'].hist(bins = 100, ax = ax)
		ax.set_xlabel('Fare per mile ($/mile)')
		ax.set_ylabel('No. of Trips')
		plt.savefig('fpm.png',format='png')
	
	print("-------------------------------------------------------------------------------------")
	print("Feature Engineering Routine Finished :-) ")
	report_change(df_in,df_out)
	print("=====================================================================================\n")

	return df_out
