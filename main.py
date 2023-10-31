import pandas as pd

# Load datasets
milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
# Enable option to display all rows when previewing
pd.set_option('display.max_columns', None)

# Clean data of unnecessary columns
cows = cows.drop(['DATAFLOW', 'LAST UPDATE', 'freq', 'month', 'animals', 'unit', 'OBS_FLAG'], axis=1)
milk_production = milk_production.drop(['DATAFLOW', 'LAST UPDATE', 'freq', 'dairyprod', 'milkitem', 'OBS_FLAG'], axis=1)

df = milk_production.merge(cows, on=['geo', 'TIME_PERIOD'], how='outer', suffixes=('_milk', '_cows'))