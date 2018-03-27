# Data science challenge C1 - Qi Li
# Predictive model module 

from standard_import import *

def run_models(df, is_gen_plots, sample_size, numbercv): 
	'''
	Predictive model for the tip percentage
	0. Inputs:  df				input dataframe				pandas.dataframe
				is_gen_plots	tag if generate plots		bool
				sample_size		size of the training set	int64
				numbercv		number of folds for CV		int64
	1. OneHotEncoder for all the categorical variables
	2. Decision Tree
	3. Random Forest
	4. Gradient Boosting Tree
	5. Cross-validation
	6. Plot the histogram of the error
	'''
	print("=====================================================================================")
	print("Predictive Model Routine Launched -------->   ")
	print("-------------------------------------------------------------------------------------\n")
	
	print("Generating the 'Tip_rate' variable:")
	df['Tip_rate'] = df['Tip_amount']/df['Total_amount']
	selected = ['VendorID', 'Hour', 'RateCodeID', 'Day_of_week', 'Payment_type', 'Tip_amount', 'Trip_distance', 'Time_span']
	categorical = ['VendorID', 'Hour', 'RateCodeID', 'Day_of_week', 'Payment_type']
	# Randomly sample the dataset
	dataset = df.sample(sample_size, random_state = 0)

	# Construct the features and the variable
	X = dataset[selected].values
	y = dataset['Tip_rate']
	
	# Performing onehotencoder for the categorical data
	onehotencoder = OneHotEncoder(categorical_features = [range(5)])
	X = onehotencoder.fit_transform(X).toarray()
	X = X[:, 1:] # To avoid the dummy variable trap, probably not necessary but I always do it

	# The grid search part is commented out to save time
	'''
	#parameters = [{'max_depth': [14], 
	#               'min_samples_split': [3]}]
	#parameters = [{'n_estimators': [55]}]
	parameters = [{'max_depth': [6]}]
	grid_search = GridSearchCV(estimator = regressor,
							   param_grid = parameters,
							   scoring = 'r2',
							   cv = 10,
							   n_jobs = -1)
	grid_search = grid_search.fit(X, y)
	best_parameters = grid_search.best_params_
	'''

	# Defining three regressors, the hyper-parameters is already optimized, grid search performed elsewhere
	regressorDT = DecisionTreeRegressor(random_state = 0, max_depth = 14, min_samples_split = 3)
	regressorRF = RandomForestRegressor(n_estimators = 60, random_state = 0, max_depth = 14)
	regressorGBM = GradientBoostingRegressor(n_estimators = 100, max_depth = 6)
	print("\nPerforming Decision Tree regressor:")
	perform_regressor(regressorDT, X, y, numbercv)
	print("\nPerforming Random Forest regressor:")
	perform_regressor(regressorRF, X, y, numbercv)
	print("\nPerforming GMB regressor:")
	perform_regressor(regressorGBM, X, y, numbercv)

	y_pred = regressorGBM.predict(X) # calculated the predicted value 
	error = y_pred - y # calculated the error

	# Plot out the error distribution
	if is_gen_plots:
		print("\nPrinting the histogram plot for error ...")
		fig, ax = plt.subplots(1,1,figsize=(6, 6))
		error.hist(bins = 100, ax = ax)
		ax.set_xlabel('Error of the predictor')
		ax.set_ylabel('Frequency')
		plt.savefig('error.png',format='png')

	print("-------------------------------------------------------------------------------------")
	print("Predictive Model Routine Finished :-) ")
	print("=====================================================================================\n")

def perform_regressor(regressor, X, y, numbercv):

	tic = pd.Timestamp.now() # take current time as the beginning of the fit
	regressor.fit(X, y) # perform the training

	# Applying k-Fold Cross Validation
	accuracies = cross_val_score(estimator = regressor, X = X, y = y, cv = numbercv)

	toc = pd.Timestamp.now() # take current time as the end of the fit
	print("Fitting and CV finished in", (toc-tic).seconds, "seconds!")
	print("Printing the results of the cross_validation:")
	print("accuracy mean: ", np.mean(accuracies))
	print("accuracy stddev: ", np.std(accuracies))
	

