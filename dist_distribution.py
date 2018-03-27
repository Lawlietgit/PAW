# Data science challenge C1 - Qi Li
# Trip distance analysis module 

from standard_import import *

def dist_analysis(df_raw, df, is_gen_plots, max_dist): # function for trip distance analysis, takes in both the raw df and the cleaned 
	'''
	Analysis of trip distance:
	0. Inputs:  df_raw			raw dataset							pandas.dataframe
				df				cleaned dataset						pandas.dataframe
				is_gen_plots	tag if or not generate the plots	bool
				max_dist		cutoff on the trip_distance			float64
	1. Plot the histogram of the overall distance distribution
	2. Plot the trip distance grouped by the hour of day
	3. Plot the trip distance and the total fare amount grouped of JFK trips
	'''
	print("=====================================================================================")
	print("Trip distance Analysis Routine Launched -------->   ")
	print("-------------------------------------------------------------------------------------\n")
	
	print("Reporting stats for the raw data:")
	report_stats(df_raw['Trip_distance'])
	print("\nReporting stats for the cleaned data:")
	report_stats(df['Trip_distance'])
		
	# Overall distribution plot
	if is_gen_plots:
		print("\nGenerating the histogram plot for \'Trip_distance\', saving to \'dist.png\' ...")
		fig1, [[ax1, ax2], [ax3, ax4], [ax5, ax6]] = plt.subplots(3, 2, figsize=(6,6))
		plt.tight_layout(pad=2.0, w_pad=0.0, h_pad=1.0)
		
		shape, loc, scale = lognorm.fit(df['Trip_distance']) # perform the lognorm fit
		xmesh = np.linspace(0.0, max_dist, 512) # create the x axis fine mesh
		fit_pdf = 305000*lognorm.pdf(xmesh, shape, loc, scale) # calculate the fitted pdf, the scale is adjusted manually

		df_raw['Trip_distance'].hist(bins = 100, ax = ax1)
		ax1.set_ylabel('No. of Trips')
		ax1.ticklabel_format(axis = 'y', style = 'sci', scilimits=(0,6))
		ax1.set_title('Raw data')

		df['Trip_distance'].hist(bins = 100, ax = ax2)
		ax2.ticklabel_format(axis = 'y', style = 'sci', scilimits=(0,5))
		ax2.plot(xmesh, fit_pdf,'r') 
		ax2.set_title('Cleaned data')

		df_raw['Trip_distance'].hist(bins = 100, ax = ax3)
		ax3.set_ylabel('No. of Trips')
		ax3.set_yscale('log')

		df['Trip_distance'].hist(bins = 100, ax = ax4)
		ax4.plot(xmesh, fit_pdf,'r') 
		ax4.set_yscale('log')

		df_raw['Trip_distance'].hist(bins = 100, ax = ax5)
		ax5.set_xlabel('Trip Distance (mile)')
		ax5.ticklabel_format(axis = 'y', style = 'sci', scilimits=(0,6))
		ax5.set_ylabel('No. of Trips')
		ax5.set_xscale('log')

		df['Trip_distance'].hist(bins = 100, ax = ax6)
		ax6.plot(xmesh, fit_pdf,'r') 
		ax6.set_xlabel('Trip Distance (mile)')
		ax6.ticklabel_format(axis = 'y', style = 'sci', scilimits=(0,5))
		ax6.set_xscale('log')
		plt.savefig('dist.png', format = 'png')
	
	# Trip distance grouped by hour of the day
	# Using pivot_table function
	print("Grouping the trip distance by hour of day using pandas.pivot_table:")
	dist_hour_mean = pd.pivot_table(df, values = ['Trip_distance'], index = ['Hour'], aggfunc = np.mean)
	dist_hour_median = pd.pivot_table(df, values = ['Trip_distance'], index = ['Hour'], aggfunc = np.median)
	
	if is_gen_plots:
		print("Generating the plot for \'Trip_distance\' grouped by \'Hour\', saving to \'dist_hour.png\' ...")
		fig2, ax = plt.subplots(1, 1, figsize=(6,6))
		ax.plot(dist_hour_mean.index, dist_hour_mean.values, label = 'mean')
		ax.plot(dist_hour_median.index, dist_hour_median.values, label = 'median')
		ax.set_xlabel('Hour of day (pick up time)')
		ax.set_ylabel('Trip distance (mile)')
		ax.legend()
		plt.savefig('dist_hour.png', format = 'png')

	# Trip from/to JFK
	print("\nBegin analysis of JFK trips:")
	print("There are", df_raw[df_raw['RateCodeID'] == 2].shape[0], "trips from/to JFK airport in the raw data.")
	print("There are", df[df['RateCodeID'] == 2].shape[0], "trips from/to JFK airport in the cleaned data.")
	jfk_raw = df_raw[df_raw['RateCodeID'] == 2] # read in the jfk trip from the raw data
	jfk_raw = jfk_raw[jfk_raw['Trip_distance'] < 50.0]
	jfk_raw = jfk_raw[jfk_raw['Total_amount'] < 100.0]
	jfk = df[df['RateCodeID'] == 2] # read in the jfk trip from the clean data
	print("\nPrinting the total fare statistical indexes of the JFK trips from the raw data:")
	report_stats(jfk_raw['Total_amount'])
	print("\nPrinting the total fare statistical indexes of the JFK trips from the clean data:")
	report_stats(jfk['Total_amount'])

	if is_gen_plots:
		print("\nGenerating histogram plots of the trip distance and total fare of JFK trips")
		fig3, [[ax1, ax2], [ax3, ax4]] = plt.subplots(2, 2, figsize=(6,6))
		plt.tight_layout(pad=4.0, w_pad=1.0, h_pad=2.0)
		
		jfk_raw['Trip_distance'].hist(bins = 20, ax = ax1)
		ax1.set_ylabel('No. of Trips')
		ax1.set_xlabel('Trip distance (mile)')
		ax1.set_title('Raw, d < 50 miles')

		jfk_raw['Total_amount'].hist(bins = 20, ax = ax3)
		ax3.set_ylabel('No. of Trips')
		ax3.set_xlabel('Total fare (dollar)')

		jfk['Trip_distance'].hist(bins = 20, ax = ax2)
		ax2.set_xlabel('Trip distance (mile)')
		ax2.set_title('Cleaned, d < 20 miles')

		jfk['Total_amount'].hist(bins = 20, ax = ax4)
		ax4.set_xlabel('Total fare (dollar)')

		plt.savefig('JFK.png', format = 'png')
	
	print("-------------------------------------------------------------------------------------")
	print("Trip distance Analysis Routine Finished :-) ")
	print("=====================================================================================\n")

