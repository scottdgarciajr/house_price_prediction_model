# Import necessary libraries
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import StackingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


# Load the training data
train_data = pd.read_csv('train.csv')

# Drop columns with too many missing values
train_data = train_data.drop(['Alley', 'PoolQC', 'Fence', 'MiscFeature'], axis=1)

# Fill missing values with appropriate values
train_data['LotFrontage'] = train_data['LotFrontage'].fillna(train_data['LotFrontage'].mean())
train_data['MasVnrType'] = train_data['MasVnrType'].fillna('None')
train_data['MasVnrArea'] = train_data['MasVnrArea'].fillna(0)
train_data['BsmtQual'] = train_data['BsmtQual'].fillna('NA')
train_data['BsmtCond'] = train_data['BsmtCond'].fillna('NA')
train_data['BsmtExposure'] = train_data['BsmtExposure'].fillna('NA')
train_data['BsmtFinType1'] = train_data['BsmtFinType1'].fillna('NA')
train_data['BsmtFinType2'] = train_data['BsmtFinType2'].fillna('NA')
train_data['Electrical'] = train_data['Electrical'].fillna('SBrkr')

# Convert categorical variables to numerical variables
train_data = pd.get_dummies(train_data)


#Get rid of outliers...

# Calculate the Z-score for each column in the training data
z_scores = (train_data - train_data.mean()) / train_data.std()

# Remove rows with a Z-score greater than 3
train_data = train_data[(z_scores < 20).all(axis=1)]


# Load the testing data
test_data = pd.read_csv('test.csv')

# Drop columns with too many missing values
test_data = test_data.drop(['Alley', 'PoolQC', 'Fence', 'MiscFeature'], axis=1)

# Fill missing values with appropriate values
test_data['LotFrontage'] = test_data['LotFrontage'].fillna(test_data['LotFrontage'].mean())
test_data['MasVnrType'] = test_data['MasVnrType'].fillna('None')
test_data['MasVnrArea'] = test_data['MasVnrArea'].fillna(0)
test_data['BsmtQual'] = test_data['BsmtQual'].fillna('NA')
test_data['BsmtCond'] = test_data['BsmtCond'].fillna('NA')
test_data['BsmtExposure'] = test_data['BsmtExposure'].fillna('NA')
test_data['BsmtFinType1'] = test_data['BsmtFinType1'].fillna('NA')
test_data['BsmtFinType2'] = test_data['BsmtFinType2'].fillna('NA')
test_data['Electrical'] = test_data['Electrical'].fillna('SBrkr')

# Convert categorical variables to numerical variables
test_data = pd.get_dummies(test_data)

# Align the columns of the training and testing data
train_data, test_data = train_data.align(test_data, join='left', axis=1, fill_value=0)

# Replace SimpleImputer with IterativeImputer
rf_imputer = IterativeImputer(estimator=RandomForestRegressor())

# Fit and transform the training data
train_data_imputed = rf_imputer.fit_transform(train_data)

# Transform the testing data
test_data_imputed = rf_imputer.transform(test_data)

# Split the training data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(train_data_imputed, train_data['SalePrice'], test_size=0.2, random_state=42)

# Define the base models
rf = make_pipeline(StandardScaler(), SimpleImputer(strategy='most_frequent'), RandomForestRegressor())
gb = make_pipeline(StandardScaler(), SimpleImputer(strategy='most_frequent'), GradientBoostingRegressor())

# Define the meta-model
meta_model = LinearRegression()

# Define the stacking regressor
stacking_regressor = StackingRegressor(
    estimators=[('rf', rf), ('gb', gb)],
    final_estimator=meta_model
)

# Train the stacking regressor on the training data
stacking_regressor.fit(X_train, y_train)

# Evaluate the model on the validation data
print('Validation score:', stacking_regressor.score(X_val, y_val))

# Make predictions on the testing data
predictions = stacking_regressor.predict(test_data_imputed)

# Save the predictions to a CSV file
submission = pd.DataFrame({'Id': 1461+test_data.index, 'SalePrice': predictions})
submission.to_csv('submission.csv', index=False)
