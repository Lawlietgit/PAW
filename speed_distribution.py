# Data science challenge C1 - Qi Li
# Trip average speed analysis module 

from standard_import import *

def speed_analysis(df, is_gen_plots, sample_size): # function for average speed analysis takes the whole dataframe
	'''
	Analysis of trip average speed distribution:
	0. Inputs:  df				input dataframe			pandas.dataframe
				is_gen_plots	tag if generate plots	bool
				sample_size		sample_size for ANOVA	int64
	1. Plot the histogram of the overall trip speed distribution
	2. ANOVA on average speed in different weeks (1-5)
	3. Plot the average speed versus hour of day
	'''
	print("=====================================================================================")
	print("Trip Speed Analysis Routine Launched -------->   ")
	print("-------------------------------------------------------------------------------------\n")
	print("Reporting stats for the trip average speed:")
	speed_mean = report_stats(df['Speed'])

	# Overall distribution plot
	if is_gen_plots:
		print("Generating the histogram plot for \'Speed\', saving to \'speed.png\' ...")

		shape, loc, scale = lognorm.fit(df['Speed']) # perform the lognorm fit
		xmesh = np.linspace(0, 40, 128) # create the x axis fine mesh
		lognorm_fit_pdf = 650000*0.94*lognorm.pdf(xmesh, shape, loc, scale) # calculate the fitted pdf, the scale is adjusted manually
		norm_fit_pdf = 455000*0.95*norm.pdf(xmesh, 11.0, 3.0) # calculate the fitted pdf, the scale is adjusted manually

		fig1, ax = plt.subplots(1,1,figsize=(6, 6))
		df['Speed'].hist(bins = 100, ax = ax)
		ax.plot(xmesh,lognorm_fit_pdf,'r', label = 'lognorm fit', linewidth = 2)
		ax.plot(xmesh,norm_fit_pdf,'k', label = 'normal fit', linewidth = 2)
		ax.set_xlabel('Average Trip Speed (mph)')
		ax.set_ylabel('No. of Trips')
		ax.legend()
		plt.savefig('speed.png',format='png')
	
	# ANOVA on the speed over weeks
	print("\nPerforming ANOVA on the speed in different weeks ...")
	week1 = df[df['Week'] == 1].sample(sample_size, random_state = 0)['Speed']
	week2 = df[df['Week'] == 2].sample(sample_size, random_state = 0)['Speed']
	week3 = df[df['Week'] == 3].sample(sample_size, random_state = 0)['Speed']
	week4 = df[df['Week'] == 4].sample(sample_size, random_state = 0)['Speed']
	week5 = df[df['Week'] == 5].sample(sample_size, random_state = 0)['Speed']
	print(f_oneway(week1, week2, week3, week4, week5))

	if is_gen_plots:
		print("\nGenerating the plot for average speed grouped by day of week ...")	
		speed_dow = pd.pivot_table(df, values = ['Speed'], index = ['Day_of_week'], aggfunc = np.mean)
		fig2, ax = plt.subplots(1,1,figsize=(6, 6))
		ax.plot(speed_dow.index,speed_dow.values, 'b', linewidth = 2)
		ax.plot([0,7], [13.027, 13.027], 'r--', linewidth = 2)
		ax.set_xlabel('Day of week')
		ax.set_ylabel('Average trip speed (mph)')
		ax.set_xlim(0,6)
		plt.savefig('speed_dow.png',format='png')

	# The average speed in a day
	speed_hour = pd.pivot_table(df, values = ['Speed'], index = ['Hour'], aggfunc = np.mean)

	if is_gen_plots:
		print("\nGenerating the plot for average speed grouped by hour of day ...")	
		fig3, ax = plt.subplots(1,1,figsize=(6, 6))
		ax.plot(speed_hour.index, speed_hour.values, 'b', linewidth = 2)
		ax.plot([0,23], [13.027, 13.027], 'r--', linewidth = 2)
		ax.set_xlabel('Hour of day')
		ax.set_ylabel('Average trip speed (mph)')
		plt.savefig('speed_hour.png',format='png')

	print("-------------------------------------------------------------------------------------")
	print("Trip Speed Analysis Routine Finished :-) ")
	print("=====================================================================================\n")

