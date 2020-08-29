# -*- coding: utf-8 -*-
"""Bank-subscription-prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18OnEf_QcBjHXAjRFKfag7ZzJOrXOHhbe

## Bank Institution Term Deposit Predictive Model

### Scenario

You successfully finished up to your rigorous job interview process with Bank of Portugal as a machine learning researcher. The investment and portfolio department would want to be able to identify their customers who potentially would subscribe to their term deposits. As there has been heightened interest of marketing managers to carefully tune their directed campaigns to the rigorous selection of contacts, the goal of your employer is to find a model that can predict which future clients who would subscribe to their term deposit. Having such an effective predictive model can help increase their campaign efficiency as they would be able to identify customers who would subscribe to their term deposit and thereby direct their marketing efforts to them. This would help them better manage their resources (e.g human effort, phone calls, time).

### Data

The data and feature description for this challenge can be found here (http://archive.ics.uci.edu/ml/datasets/Bank+Marketing).

### Table of content
1. Importing the necessary libraries
2. Data importation
3. 
4.

#### Importing the necessary libraries
"""

# Commented out IPython magic to ensure Python compatibility.
# Imports

# pandas
import pandas as pd
from pandas import Series,DataFrame

# os
import os

# numpy, matplotlib, seaborn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')

# %matplotlib inline

# warnings
import warnings
warnings.filterwarnings('ignore')

# sklearn packages
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

# Class imbalance
from imblearn.over_sampling import RandomOverSampler
from collections import Counter

"""First, we need to import the path with raw data"""

# setting the raw path
raw_data_path = os.path.join(os.path.pardir,"data","raw")
bank_file_path = os.path.join(raw_data_path,"bank-additional-full.csv")

"""Now we import the Bank data"""

bank_data = pd.read_csv(bank_file_path,sep = ';')

"""#### Data Understanding
Let us know have a glance at how our data looks like and it's structure.
"""

bank_data.info()

bank_data.head()

"""###   Below is the Variable description of the Bank dataset
| variable         | description |
| ---------------- | ------------|
`Bank client data`
| `age`         | client's age (numeric)                                                |<br>
| `job`         | type of job (categorical)                                             |<br>
| `marital`     | marital status (categorical                                           |<br>
| `education`   | education level (categorical)                                         |<br>
| `default`     | if client has credit in default (categorical)                         |<br>
| `housing`     | if client has housing loan (categorical)                              |<br>
| `loan`        | if client has personal loan (categorical)                             |<br>

|`Related with last contact of the current campaign`<br>|
| `contact`     | contact communication type (categorical)                              |<br>
| `month`       | last contact month of the year (categorical)                          |<br>
| `day_of_week` | last contact day of the week (categorical)                            |<br>
| `duration`    | last contact duration, in seconds (numeric)                           |<br> 

`Other attributes`<br>
| `campaign`    | number of contacts performed during this campaign and for this client |<br> 
| `pdays`       | number of days that passed by after the client was last contacted from a previous campaign |<br>
| `previous`    | number of contacts performed before this campaign and for this client (numeric) |<br>
| `poutcome`    | outcome of the previous marketing campaign (categorical) |<br>

`Social and economic context attributes`<br>
| `emp.var.rate`   | employment variation rate - quarterly indicator (numeric) |<br>
| `cons.price.idx` | consumer price index - monthly indicator (numeric)        |<br>
| `cons.conf.idx`  | consumer confidence index - monthly indicator (numeric)   |<br>
| `euribor3m`      | euribor 3 month rate - daily indicator (numeric)          |<br>
| `nr.employed`    | number of employees - quarterly indicator (numeric)       |<br>
"""

bank_data.shape

#Checking the data datatypes.
bank_dtypes = pd.DataFrame(bank_data.dtypes,columns =["Data_Type"] )

bank_dtypes

class Information:
    def __init__(self):
        """
        This class give some brief information about the datasets.
        """
        print("Information object created")
    
    def _get_missing_values(self,data):
        """
        Find missing values of given datad
        :param data: checked its missing value
        :return: Pandas Series object
        """
        #Getting sum of missing values for each feature
        missing_values = bank_data.isnull().sum()
        #Feature missing values are sorted from few to many
        missing_values.sort_values(ascending=False, inplace=True)

        #Returning missing values
        return missing_values
    
    def _get_unique_values(self,data):
        #Getting unique alues for each feature
        unique_values = bank_data.nunique()
        #Sorting the values
        unique_values.sort_values(ascending=False, inplace=True)
        
        #Returning unique values values
        return unique_values

bank_info = Information()
bank_info._get_unique_values(bank_data)

bank_info._get_missing_values(bank_data)

# Summary of the numerical columns
bank_data.select_dtypes(include=["int64", "float64"]).describe().T

# Summary of the categorical columns
bank_data.select_dtypes(include=["object"]).describe().T

"""Great, our data has no missing values, now we can check out for the outliers."""

#Defining the path to save the figures/plots.
figures_data_path = os.path.join(os.path.pardir, 'reports','figures')

def outlier_vars(data, show_plot=True):
    
    """
    This functions checks for columns with outlers using the IQR method
    
    It accespts as argmuent a dataset. 
    show_plot can be set to True to output pairplots of outlier columns
    
    """
    
    outliers = []
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    num_data = data.select_dtypes(include='number')
    result = dict ((((num_data < (Q1 - 1.5 * IQR)) | (num_data > (Q3 + 1.5 * IQR)))==True).any())
    for k,v in result.items():
        if v == True:
            outliers.append(k)
    if show_plot:
        pair_plot = sns.pairplot(data[outliers]);
        print(f'{result},\n\n Visualization of outlier columns')
        return pair_plot
    else:
        return data[outliers]
    #my_outliers = result + '.png'
    #plt.savefig(os.path.join(figures_data_path, my_outliers))
    
outlier_vars(bank_data)

"""### Univariate Analysis

`Target variable : y`
"""

sns.catplot(x ="y",data = bank_data,kind ="count")
plt.title("Distribution of the target variable")
plt.savefig("target_variable.png")
plt.show()

"""More clients did not subscribe compared to the one's who did not subscribe. This is an instance of class imbalance.
When the dataset has underrepresented data(in this case the class yes), the class distribution starts skew. To deal with this we are going to to use Random Oversampler mehod to deal with the imbalanced data.

`Marital`
"""

sns.catplot(x ="marital",data = bank_data,kind ="count")

"""`job`"""

plt.rcParams['figure.figsize'] = (10, 5)
sns.catplot(x ="job",data = bank_data,kind ="count")
plt.xticks(rotation = 75)

"""`education`"""

sns.catplot(x ="education",data = bank_data,kind ="count")
plt.xticks(rotation = 75)

"""`default`"""

sns.catplot(x = "default",data = bank_data,kind ="count")

bank_data.hist(bins= 10, figsize=(14, 10))
plt.savefig("Distribution.png")
plt.show()

"""Observation:The age distribution is skewed to the left. Most clients are on their late 20's and Thirties.

## Bivariate Analysis
"""

def boxplot(x, y, data=bank_data, hue= "y"):
    plot = sns.boxplot(x= x, y=y, hue=hue, data= bank_data)
    plt.xticks( rotation=45, horizontalalignment='right' )
    plt.title("Boxplot of " + " " + x.upper() + " " + "and "+ " " + y.upper())
    plt.savefig("boxplot.png")
    return plot

"""`marital satus vs age and target`"""

boxplot("marital", "age", data=bank_data, hue= "y")

"""`education level vs age and target`"""

boxplot("education", "age", data=bank_data, hue= "y")

f,ax=plt.subplots(1,2, figsize=(14,6))
labels = 'Declined', 'Accepted'
bank_data['y'].value_counts().plot.pie(explode=[0,0.1],autopct='%1.1f%%',ax=ax[0],shadow=True,labels=labels,fontsize=14)
ax[0].set_title('Term Deposits', fontsize=20)
ax[0].set_ylabel('Total Clients', fontsize=14)
sns.countplot('y',data=bank_data,ax=ax[1])
ax[1].set_title('Term Deposits', fontsize=20)
ax[1].set_xticklabels(['Declined', 'Accepted'], fontsize=12)
plt.savefig("Ditribution of Term Deposits.png")
plt.show()

"""#### Correlation matrix"""

bank_data.corr()

correlation_df = bank_data
corr_table = correlation_df.iloc[:, :].corr()
corr_table
plt.figure(figsize=(16,8))
ax = sns.heatmap(corr_table, annot=True,
                fmt=".3f",
                annot_kws={'size':12},
                cmap="YlGnBu")
plt.title('Correlation matrix', fontsize=18)
plt.tight_layout
plt.xticks(rotation = 25)
plt.savefig("Correlation_heatmap.png")
plt.show()

"""## Data Preprocessing.

`Duration` attribute highly affects the output target (e.g., if duration=0 then y='no'). Yet, the duration is not known before a call is performed. Also, after the end of the call y is obviously known. Thus, this input should only be included for benchmark purposes and shall be discarded if the intention is to have a realistic predictive model.
"""

def preprocess(data):
    data = data.drop(["duration"],axis = 1)
    
    data['education'].replace({'basic.9y': 'basic','basic.4y': 'basic','basic.6y':'basic','unknown':'illiterate'},inplace=True)
    
    data['job'].replace({'self-employed':'entrepreneur'},inplace=True)

    return data

bank_df = preprocess(bank_data)

bank_df["education"].value_counts()

"""### Categorical Feature encoding

`Binary Encoding`
"""

# y column
bank_df['subscription'] = np.where(bank_df.y == 'yes', 1, 0)

# OneHotEncoding
bank_df = pd.get_dummies(bank_df, columns=['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month',
                                'day_of_week', 'poutcome'])

#dropping the y variable
bank_df = bank_df.drop(['y'], axis=1)

# reorder columns
columns = [column for column in bank_df.columns if column != 'subscription']
columns = ['subscription'] + columns 
bank_df = bank_df[columns]

"""### Numerical feature scaling"""

# Select numerical columns
numeric_columns = ['emp.var.rate',"pdays","age", 'cons.price.idx','cons.conf.idx', 'euribor3m', 'nr.employed']

scaler = StandardScaler()
bank_df[numeric_columns] = scaler.fit_transform(bank_df[numeric_columns])

bank_df.head()

"""### Removing The outliers : 
Outliers can skew statistical measures and data distributions, providing a misleading representation of the underlying data and relationships. Removing outliers from training data prior to modeling can result in a better fit of the data and, in turn, more skillful predictions.
"""

# Create independent and Dependent features
columns = bank_df.columns.tolist()
# Filter the columns to remove data we do not want
columns = [c for c in columns if c not in ["subscription"]]
# Store the variable we are predicting
target = "subscription"
# Define a random state
state = np.random.RandomState(42)
X = bank_df[columns]
y = bank_df[target]
X_outliers = state.uniform(low=0, high=1, size=(X.shape[0], X.shape[1]))
# print the shapes of X and Y
print(X.shape)
print(y.shape)

"""### Dealing with Imbalanced data: Random Over-sampling Technique
Overview; 
Random resampling provides a naive technique for rebalancing the class distribution for an imbalanced dataset.Random oversampling duplicates examples from the minority class in the training dataset.In our case we are going to duplicate the examples in the minority class which is the `yes` class to ensure we have a balanced data.
"""

def catplot(x,data):
    plot= sns.catplot(x, kind="count", data=data, palette="Set1")
    plt.xticks(rotation=45, horizontalalignment='right' )
    plt.title("counts"+ " "+ "of" + " "+ " " + x )
    return 
catplot("subscription",data = bank_df)

# Defuining the random sampler function.
ros = RandomOverSampler(random_state=42)
X_train_res, y_train_res = ros.fit_resample(X, y)

print('After OverSampling, the shape of train_X: {}'.format(X_train_res.shape))
print('After OverSampling, the shape of train_y: {} \n'.format(y_train_res.shape))

X_train_res.head()

"""## Data Transformation:Dimensionality reduction
### Principal Component Analysis
The main linear technique for dimensionality reduction, principal component analysis, performs a linear mapping of the data to a lower-dimensional space in such a way that the variance of the data in the low-dimensional representation is maximized
"""

from sklearn.decomposition import PCA

pca = PCA(n_components = 10)
pca.fit(X_train_res)
X = pca.transform(X_train_res)

principal_Df = pd.DataFrame(data = X
             , columns = ['PC_1', 'PC_2','PC_3', 'PC_4','PC_5','PC_6', 'PC_7',
                          'PC_8', 'PC_9','PC_10'])
principal_Df

print('Explained variation per principal component: {}'.format(pca.explained_variance_ratio_))

df = pd.DataFrame({'var':pca.explained_variance_ratio_,
             'PC':['PC_1', 'PC_2','PC_3', 'PC_4','PC_5','PC_6', 'PC_7',
                          'PC_8', 'PC_9','PC_10']})
sns.barplot(x='PC',y="var", 
           data=df, color="c")
plt.xlabel("Components")
plt.ylabel("Variance explained by the components")
plt.title("A scree plot of the principle components")
plt.savefig("A plot of variance explained by Components.png")
plt.show()

"""Now let's save the preprocessed data for use in modeling"""

processed_data_path = os.path.join(os.path.pardir, 'data','processed')
write_train_path = os.path.join(processed_data_path, 'train.csv')
write_test_path = os.path.join(processed_data_path, 'test.csv')

# train data
principal_Df.to_csv(write_train_path,index = False)
#test data
y_train_res.to_csv(write_test_path,index = False)

"""### Pipeline building
The first step in building the pipeline is to define each transformer type. The convention here is generally to create transformers for the different variable types.The categorical transformer also has a SimpleImputer with a different fill method, and leverages OneHotEncoder to transform the categorical values into integers.
Then, Next we use the ColumnTransformer to apply the transformations to the correct columns in the dataframe. Before building this wem have stored lists of the numeric and categorical columns using the pandas dtype method.
"""

'''
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# Select categorical columns with relatively low cardinality (convenient but arbitrary)
categorical_features = [cname for cname in bank_data.drop(['y'], axis=1).columns if 
                    bank_data[cname].dtype == "object"]

# Select numerical columns
numeric_features = [cname for cname in bank_data.columns if 
                bank_data[cname].dtype in ['int64', 'float64']]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])
'''