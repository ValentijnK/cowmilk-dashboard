import pandas as pd

milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
pd.set_option('display.max_columns', None)



print(cows.head(10))
print(milk_production.head(10))