import pandas as pd
import streamlit as st
import time

milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
pd.set_option('display.max_columns', None)

milk_production = milk_production[milk_production['dairyprod'].isin(['D1110A'])]
milk_production = milk_production[milk_production['TIME_PERIOD'].isin([2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2021, 2022])]

# drop columns
milk_production = milk_production.drop(columns=['DATAFLOW', 'LAST UPDATE', 'freq', 'dairyprod', 'milkitem', 'OBS_FLAG'])
milk_production = milk_production.rename(columns={'TIME_PERIOD': 'year', 'geo': 'country', 'OBS_VALUE': 'milk_production'})
cows = cows.drop(columns=['DATAFLOW', 'LAST UPDATE', 'freq', 'animals', 'month', 'unit', 'OBS_FLAG'])
cows = cows.rename(columns={'TIME_PERIOD': 'year', 'geo': 'country', 'OBS_VALUE': 'cows'})

# Check for duplicate values
# print("Duplicates in milk_production:", milk_production.duplicated().sum())
# print("Duplicates in cows:", cows.duplicated().sum())

# Merge the two dataframes
df = pd.merge(milk_production, cows, on=['country', 'year'])

# Parse years to datetime
df['year'] = pd.to_datetime(df['year'], format='%Y', errors='coerce')
print(df)
st.set_page_config(
    page_title='Hoeveel melk geeft een koe?',
    layout='wide'
)

title_col, datepicker_col, country_col = st.columns(3)
# Get the first and last date of the data to limit datapicker entries
start_year = df['year'].min()
end_year = df['year'].max()
with title_col:
    st.title('Hoeveel melk geeft een koe?')
# Create Datepicker element
with datepicker_col:
    date = st.date_input(
        "Selecteer periode",
        (start_year, end_year),
        start_year,
        end_year
    )
# Fill variables from datepicker tuple
try:
    filter_start, filter_end = date
except ValueError:
    with st.spinner("Even denken.."):
        time.sleep(10)
        st.stop()

with country_col:
    country_list = pd.unique(df['country'])
    country = st.selectbox(
        'Kies een land',
        (country_list)
    )
st.write(country)
# Subset Dataframe based on datepicker
filtered_year = df[(df['year'] >= pd.to_datetime(filter_start))
                             & (df['year'] <= pd.to_datetime(filter_end))]
filtered_data = filtered_year[filtered_year['country'] == country]
st.write(filtered_data)
# Container 2: Metrics
metric1, metric2, metric3, metric4 = st.columns(4)
# Get total liters of milk produced
total_milk = (filtered_data['milk_production'].sum() * 1000)
# Get average numbers of livestock
# total_cows =

consumption = filtered_data['TotalEnergy'].sum()
avg_eff = filtered_data['Efficiency'].mean()

# Compute value to kWh or MWh based on the consumption
# def compute_cows(kW):
#     if kW == 0:
#         return f" { 0.0 } MWh"
#     elif kW > 0:
#         if math.floor(math.log10(abs(kW))) >= 3:
#             return f" {round((kW / 1000), 2)} MWh"
#         else:
#             return f" {round(kW, 2)} kWh"
#     else:
#         if math.floor(math.log10(abs(kW))) >= 3:
#             return f" {round((kW / 1000), 2)} MWh"
#         else:
#             return f" {round(kW, 2)} kWh"


# metric1.metric(
#     label='Prod. Melk',
#     value=f" {int(hours_charge)} uur {int(minutes_charge)} min",
#     delta=f"{int(hours_charge) - int(st.session_state['charge_hours'])} uur {int(minutes_charge) - int(st.session_state['charge_minutes'])} min",
#     delta_color='off'
# )
# metric2.metric(
#     label='Gem. Tijd aan de laadpaal',
#     value=f" {int(hours_conn)} uur {int(minutes_conn)} min",
#     delta=f"{int(hours_conn) - int(st.session_state['conn_hours'])} uur {int(minutes_conn) - int(st.session_state['conn_minutes'])} min",
#     delta_color='off'
# )
# metric3.metric(
#     label='Gem. Efficientie',
#     value=f"{round(avg_eff, 2)} %",
#     delta=f"{round(avg_eff - st.session_state['efficiency'], 2)}%"
# )
# metric4.metric(
#     label='Totaal Opgeladen',
#     value=compute_kW(consumption),
#     delta=compute_kW((consumption - st.session_state['consumption']))
# )
