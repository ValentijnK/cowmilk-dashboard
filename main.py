import pandas as pd
import streamlit as st
import time
import plotly.express as px
import country_converter as coco


milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
pd.set_option('display.max_columns', None)

milk_production = milk_production[milk_production['dairyprod'].isin(['D1110A'])]

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
    country = st.multiselect(
        'Kies een land',
        (country_list)
    )
# Subset Dataframe based on datepicker
filtered_year = df[(df['year'] >= pd.to_datetime(filter_start))
                             & (df['year'] <= pd.to_datetime(filter_end))]


filtered_data = filtered_year[filtered_year['country'].isin(country)]
# Container 2: Metrics
if len(country) > 1:
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    country_1 = filtered_data[filtered_data['country'] == country[0]]
    country_2 = filtered_data[filtered_data['country'] == country[1]]

    total_milk_c1 = round((country_1['milk_production'].sum() * 1000), 2)
    total_milk_c2 = round((country_2['milk_production'].sum() * 1000), 2)

    avg_cows_c1 = round((country_1['cows'].mean() * 1000), 2)
    avg_cows_c2 = round((country_2['cows'].mean() * 1000), 2)

    milk_per_cow_c1 = round((total_milk_c1 / avg_cows_c1) * 1000, 2)
    milk_per_cow_c2 = round((total_milk_c2 / avg_cows_c2) * 1000, 2)

    m1.metric(
        label=f"Prod. Melk - {country[0]}",
        value=f"{total_milk_c1:,}",
    )
    m2.metric(
        label=f"Prod. Melk - {country[1]}",
        value=f"{total_milk_c2:,}",
    )
    m3.metric(
        label=f"Gem. aantal koeien - {country[0]}",
        value=f"{avg_cows_c1:,}"
    )
    m4.metric(
        label=f"Gem. aantal koeien - {country[1]}",
        value=f"{avg_cows_c2:,}",
    )
    m5.metric(
        label=f"Aantal liter per koe - {country[0]}",
        value=f"{milk_per_cow_c1:,}"
    )
    m6.metric(
        label=f"Aantal liter per koe - {country[1]}",
        value=f"{milk_per_cow_c2:,}"
    )
elif len(country) == 1:
    m1, m2, m3 = st.columns(3)
    # Get total liters of milk produced
    total_milk = round((filtered_data['milk_production'].sum() * 1000), 2)
    # Get average numbers of livestock
    avg_cows = round((filtered_data['cows'].mean() * 1000), 2)
    # milk produced per cow
    milk_per_cow = round((total_milk / avg_cows) * 1000, 2)
    m1.metric(
        label='Prod. Melk',
        value=f"{total_milk:,}",
        # delta=f"{int(hours_charge) - int(st.session_state['charge_hours'])} uur {int(minutes_charge) - int(st.session_state['charge_minutes'])} min",
    )
    m2.metric(
        label='Gem. aantal koeien',
        value=f"{avg_cows:,}",
        # delta=f"{int(hours_conn) - int(st.session_state['conn_hours'])} uur {int(minutes_conn) - int(st.session_state['conn_minutes'])} min",
        delta_color='off'
    )
    m3.metric(
        label='Aantal liter per koe',
        value=f"{milk_per_cow:,}",
        # delta=f"{round(avg_eff - st.session_state['efficiency'], 2)}%"
    )


fig_col1, fig_col2 = st.columns(2)
with fig_col1:
    st.markdown('### Productie van melk over de jaren')
    fig_line = px.line(filtered_data, x='year', y='milk_production', color='country')
    fig_line.update_layout(
        yaxis_title='Aantal liter (x1000)',
        xaxis_title='Jaar'
    )
    st.plotly_chart(fig_line, theme='streamlit')

    # st.line_chart(df_grouped_day, y='TotalEnergy')
# with fig_col2:
#     st.markdown('### Efficiency occurrence')
#     fig = px.histogram(filtered_data, x='Efficiency', nbins=10)
#     fig.update_xaxes(range=[0, 100], title='Efficiency')
#     st.plotly_chart(fig)








# filtering for maps
year = 2022
df['country'] = df['country'].replace('EL', 'GR') # Greece
country = coco.convert(names=df['country'], to="ISO3")
df['country_ISO3'] = country
mapdf = df.groupby(['milk_production', 'cows', 'country_ISO3', 'year']).size().reset_index()
mapdf = mapdf[mapdf['country_ISO3'] != 'not found'] # remove not found (total eu values)
filtered_mapdf = mapdf[mapdf['year'] == year]

# MELK PRODUCTIE
fig = px.choropleth(locations=filtered_mapdf['country_ISO3'], color=filtered_mapdf['milk_production'], scope='europe',
                    color_continuous_scale='RdYlGn', title=f'Milk production in Europe in {year}')
st.plotly_chart(fig)
# AANTAL KOE
fig1 = px.choropleth(locations=filtered_mapdf['country_ISO3'], color=filtered_mapdf['cows'], scope='europe',
                    color_continuous_scale='RdYlGn', title=f'Koe in Europa in {year}')
st.plotly_chart(fig1)

