import numpy as np
import pandas as pd
import streamlit as st
import time
import plotly.express as px
import country_converter as coco
from PIL import Image
import folium
from streamlit_folium import st_folium
import statsmodels.api as sm


milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
information = pd.read_csv('milk_industry.csv', sep=';')
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
# Set correct country code
df['country'] = df['country'].replace('EL', 'GR')
# Drop outlier
df.drop(df[df['country'] == 'EU27_2020'].index, inplace=True)
# Feature Engineering
df['milk_production'] = df['milk_production'] * 1000
df['cows'] = df['cows'] * 1000
df['milk_per_cow'] = ((df['milk_production']) / (df['cows'])) * 1000



st.set_page_config(
    page_title='Welk land produceert de meeste melk in Europa?',
    layout='wide'
)
with st.container():
    title_col, col_right = st.columns(2)
    with title_col:
        st.title('Welk land produceert de meeste melk in Europa?')
        '''
            Nieuwsgierig naar melkproductie in Europa? Ons dashboard heeft je gedekt! Kies gewoon een jaartal en bepaal
            zelf hoeveel Europese landen je wilt verkennen. Hier kun je ontdekken hoeveel koeien er gemiddeld zijn, hoeveel 
            melk ze produceren en zelfs hoe productief elke koe is in het land dat je kiest. Dompel jezelf onder in de wereld 
            van Europese melkproductie en ontrafel de geheimen van deze smakelijke sector!
        '''
    with col_right:
        image = Image.open('cow.jpg')
        st.image(image, width=200)
    st.divider()
    expander1 = st.expander("Hoe gebruik ik het dashboard?")
    expander1.write('Selecteer hieronder een of meerdere jaren en de landen die u wilt vergelijken. '
                   'Let op dat u als een jaar wilt selecteren minimaal de periode neemt die een jaar bestrijkt. '
                   'Voorbeeld: 1 jan 2016 - 1 jan 2017. Het dashboard is het voornamelijk ingericht om twee landen met elkaar te vergelijken.')
    expander2 = st.expander("Waarom staat het Verenigd Koninkrijk in de lijst?")
    expander2.write('Het Verenigd Koninkrijk heeft op 31 januari 2020 de Europese Unie verlaten. Data tot aan die datum is nog beschikbaar en wordt ook getoond in dit dashboard.')

    datepicker_col, country_col = st.columns(2)
    # Get the first and last date of the data to limit datapicker entries
    start_year = df['year'].min()
    end_year = df['year'].max()
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
        country_list = np.append(country_list, 'Alle')
        country = st.multiselect(
            'Kies een land',
            (country_list),
            default=['NL', 'DE']
        )
# Subset Dataframe based on datepicker
filtered_year = df[(df['year'] >= pd.to_datetime(filter_start))
                             & (df['year'] <= pd.to_datetime(filter_end))]
try:
    if country[0] == 'Alle':
        filtered_data = filtered_year[filtered_year['country'].isin(pd.unique(df['country']))]
    else:
        filtered_data = filtered_year[filtered_year['country'].isin(country)]
except IndexError:
    st.stop()


# Calculate values for metrics
if len(country) > 1 & len(country) < 2:
    country_1 = filtered_data[filtered_data['country'] == country[0]]
    country_2 = filtered_data[filtered_data['country'] == country[1]]

    total_milk_c1 = round((country_1['milk_production'].sum()), 2)
    total_milk_c2 = round((country_2['milk_production'].sum()), 2)

    avg_cows_c1 = round((country_1['cows'].mean()), 2)
    avg_cows_c2 = round((country_2['cows'].mean()), 2)

    milk_per_cow_c1 = round(filtered_data[filtered_data['country'] == country[0]]['milk_per_cow'].mean(), 2)
    milk_per_cow_c2 = round(filtered_data[filtered_data['country'] == country[1]]['milk_per_cow'].mean(), 2)


elif len(country) == 1:
    # Get total liters of milk produced
    total_milk = round((filtered_data['milk_production'].sum()), 2)
    # Get average numbers of livestock
    avg_cows = round((filtered_data['cows'].mean()), 2)
    # milk produced per cow
    milk_per_cow = round((total_milk / avg_cows), 2)


# Get information based on country code
info = information[information['country'].isin(country)]
info_col, rank_col = st.columns(2)
with info_col:
    if len(country) == 0:
        st.stop()
    elif country[0] == 'Alle':
        f'''
        # Europa
        '''
    else:
        countries = coco.convert(names=country, src='ISO2', to='name_short')
        if isinstance(countries, list) == 0:
            f'''
                # {countries}
            '''
        elif len(countries) == 2:
            f'''
            # {countries[0]} VS. {countries[1]}
            '''
        else:
            f'''
            ### Europa: {' VS. '.join(countries)}
            '''
    if country[0] != 'Alle':
        for i in info['info']:
            f'''
            **{i}**
            '''
    else:
        f'''
            {info['info'].iloc[-1]}
        '''
with rank_col:
    grouped_df = filtered_data.groupby(by='country', as_index=False)['milk_per_cow'].mean()
    scoreboard = grouped_df.sort_values(by='milk_per_cow', ascending=False, ignore_index=True)
    scoreboard = scoreboard.head(5)
    '''
    # Ranking the cows :cow2:
    '''
    for i, row in scoreboard.iterrows():
        score = i + 1  # The score increments from 1
        c = row['country']
        milk_per_cow = round(row['milk_per_cow'])
        st.write(f"### #{score} {c} - {milk_per_cow} liter")


st.divider()

# Container 2: Metrics
if len(country) == 2:
    m1, m2, m3, m4, m5, m6 = st.columns(6)

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

    m1.metric(
        label='Prod. Melk',
        value=f"{total_milk:,}"
    )
    m2.metric(
        label='Gem. aantal koeien',
        value=f"{avg_cows:,}"
    )
    m3.metric(
        label='Aantal liter per koe',
        value=f"{milk_per_cow:,}"
    )


fig_col1, fig_col2 = st.columns(2)
with fig_col1:
    st.markdown('### Productie van melk')
    fig_line = px.line(filtered_data, x='year', y='milk_production', color='country')
    fig_line.update_layout(
        yaxis_title='Aantal liter',
        xaxis_title='Jaar'
    )
    st.plotly_chart(fig_line, theme='streamlit')


with fig_col2:
    st.markdown('### Aantal koeien')
    fig_line = px.line(filtered_data, x='year', y='cows', color='country')
    fig_line.update_layout(
        yaxis_title='Aantal koeien',
        xaxis_title='Jaar'
    )
    st.plotly_chart(fig_line, theme='streamlit')

st.divider()
col3, fig_col4, fig_col5 = st.columns(3)
with col3:
    '''
        ## Hoe productief is een koe? 	:chart_with_upwards_trend:
         De grafieken aan de rechterkant van deze visualisatie tonen de gemiddelde melkproductie per koe in verschillende
         Europese landen. Deze gegevens zijn verkregen door de totale hoeveelheid geproduceerde melk in elk land te delen door het aantal melkkoeien.

        Wat opvalt, is dat er aanzienlijke variatie is in de melkproductie per koe in de verschillende Europese landen. Sommige landen bereiken aanzienlijk hogere productiviteit per koe dan andere.
        
        Deze gegevens dagen de kijker uit om verschillende conclusies te trekken en vragen te stellen, zoals:

        * Waarom zijn sommige landen veel efficiënter in de melkproductie per koe dan andere?
        
        * Spelen klimatologische omstandigheden, landbouwpraktijken of het gebruik van technologie een rol in deze variatie?
        
        * Hoe beïnvloedt deze variatie de economie en landbouw in elk land?
        
        * Zijn er lessen die we kunnen leren van de landen met de hoogste melkproductie per koe?
        '''
        

with fig_col4:
    fig_line = px.line(filtered_data, x='year', y='milk_per_cow', color='country')
    fig_line.update_layout(
        title_text='Melk per koe',
        yaxis_title='Melk productie per koe',
        xaxis_title='Jaar'
    )
    st.plotly_chart(fig_line, theme='streamlit')

with fig_col5:
    # lineplot
    jaar_selectie = st.select_slider("Kies een jaar",
                                     options=filtered_data['year'].dt.year.unique())

    milk_cow_country_year = filtered_data[filtered_data['year'].dt.year == jaar_selectie]

    fig = px.scatter(milk_cow_country_year, x='cows', y="milk_production", color='country')
    fig.update_layout(
        title_text='Aantal liter melk geproduceerd en aantal koeien per land per jaar',
        xaxis_title_text='Aantal koeien',
        yaxis_title_text='Aantal liter melk geproduceerd'
    )
    st.plotly_chart(fig)

info_col, fig_col6, fig_col7 = st.columns(3)
with info_col:
    '''
    ### Interessant? Lees hieronder meer!
        '''
    uitleg1 = st.expander("Uitleg: Efficienter of gewoon anders?")
    uitleg1.write('De efficiëntie van melkproductie kan variëren om verschillende redenen. Een belangrijke factor is'
                      ' de selectie en het fokken van melkkoeien om de melkopbrengst te maximaliseren. Andere factoren zijn'
                      ' de voeding van de koeien, gezondheidszorgpraktijken en de algehele landbouwbeheersing. '
                      'Landen die deze aspecten optimaliseren, zijn waarschijnlijk efficiënter in melkproductie.')
    uitleg2 = st.expander("Uitleg: Klimaat en melkproductie")
    uitleg2.write('Ja, deze factoren spelen zeker een rol. Klimatologische omstandigheden kunnen van invloed zijn op de '
                  'beschikbaarheid van weidegrond en voeder, wat van invloed is op de voeding van de koeien. '
                  'Landbouwpraktijken, zoals het gebruik van moderne technologie en managementmethoden, kunnen de efficiëntie verhogen. '
                  'Landen die deze elementen in evenwicht brengen, kunnen betere resultaten behalen.')
    uitleg3 = st.expander("Uitleg: Economische voorsprong?")
    uitleg3.write('De variatie in melkproductie per koe kan aanzienlijke economische gevolgen hebben. '
                  'Landen met efficiëntere melkproductie kunnen een grotere productie realiseren en mogelijk exporteren'
                  'naar internationale markten. Dit kan bijdragen aan economische groei en handelsvoordelen. '
                  'Bovendien heeft de landbouwsector in deze landen de potentie om arbeidskansen te creëren.')
    uitleg4 = st.expander("Uitleg: En hoe zit het met die lessen?")
    uitleg4.write('Ja, landen met hoge melkproductie per koe kunnen best practices bieden voor anderen. '
                  'Dit kan onder meer betrekking hebben op genetica, voedingsstrategieën, diergezondheid en landbouwbeheer. '
                  'Het delen van kennis en ervaringen tussen landen kan bijdragen aan verbeteringen in de '
                  'melkproductiesector wereldwijd en helpen om de efficiëntie te vergroten.')


with fig_col6:
    fig6 = px.box(filtered_data, x='country', y='cows',
                 color='country')
    fig6.update_layout(
        title='Boxplot voor aantal koeien per land',
        xaxis_title_text='Land',
        yaxis_title_text='Aantal koeien'
    )
    st.plotly_chart(fig6)

with fig_col7:
    fig7 = px.box(filtered_data, x='country', y='milk_production',
                 color='country')
    fig7.update_layout(
        title='Boxplot voor aantal geproduceerd melk per jaar',
        xaxis_title_text='Land',
        yaxis_title_text='Aantal liter melk geproduceerd')
    st.plotly_chart(fig7)
st.divider()

# year = pd.to_datetime('2022', format='%Y')
country = coco.convert(names=df['country'], to="ISO3")
df['country_ISO3'] = country
mapdf = df.groupby(['milk_production', 'cows', 'milk_per_cow', 'country_ISO3', 'year']).size().reset_index()
mapdf = mapdf[mapdf['country_ISO3'] != 'not found']  # remove not found (total EU values)
year = st.select_slider("Kies een jaar", options=mapdf['year'].dt.year.unique()[::-1], value=2022)
year = pd.to_datetime(year, format='%Y')
filtered_mapdf = mapdf[mapdf['year'] == year]

info_map, map_milk, map_cows, map_milk_per_cow = st.columns(4)
with info_map:
    '''
    # Op de kaart! 	:world_map:
    
    Houdt jij ook zo van kleurrijke kaarten? Wij ook! In dit stukje gaan we het hebben over melkproductie in Europa en hoe kleurrijke kaarten ons inzicht kunnen geven in de productie van melk en het aantal koeien in verschillende regio's.
    
    Europa is een van 's werelds belangrijkste regio's als het gaat om melkproductie. De Europese Unie, met zijn gevarieerde klimaat- en geografische omstandigheden, biedt de perfecte omgeving voor het houden van melkkoeien en de productie van zuivelproducten. Kaarten kunnen ons helpen begrijpen waar deze productie zich concentreert en welke gebieden de grootste bijdrage leveren aan de Europese melkindustrie.
    
    Laten we eens kijken naar enkele kleurrijke kaarten die ons inzicht verschaffen in de melkproductie en het aantal koeien in Europa:
    
    **De Melkproductiekaart:** Deze kaart laat zien welke Europese landen de hoogste melkproductie hebben. De kleuren op de kaart geven aan waar de productie het meest geconcentreerd is. Je zult merken dat landen zoals Duitsland, Frankrijk, Nederland en Ierland prominent aanwezig zijn op deze kaart, met intense kleuren die hun sterke melkproductie weerspiegelen.
    
    **Koeiendichtheidkaart:** Deze kaart toont ons waar de meeste koeien in Europa worden gehouden. De kleuren op deze kaart geven ons een idee van de concentratie van koeien verschillende landen. Gebieden met een hoge koeiendichtheid, zoals delen van Nederland en delen van het noorden van Spanje, worden aangegeven door levendige kleuren.
    
    **Mellproductie per koe:** De laatste kaart toont de melkproductie per koe per land. Hier kun je zien in welk land de meest productieve koeien grazen! 
    '''
# Milk production
with map_milk:
    map1 = folium.Map(location=[48, 12], zoom_start=4, tiles='cartodbpositron', width=500)
    folium.Choropleth(
        geo_data='countries.geojson',
        data=filtered_mapdf,
        columns=['country_ISO3', 'milk_production'],
        key_on='properties.ISO_A3',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Milk production in Europe',
    ).add_to(map1)
    st_data = st_folium(map1)


# CHECK FF WAT HIER NOG MOET GEBEUREN. DIE MAP TANKT HEEL DIE SERVER LEEG
# GG gefixed
# AANTAL KOE -- my god
with map_cows:
    map = folium.Map(location=[48, 12], zoom_start=4, tiles='cartodbpositron')
    folium.Choropleth(
        geo_data='countries.geojson',
        data=filtered_mapdf,
        columns=['country_ISO3', 'cows'],
        key_on='properties.ISO_A3',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Cows in Europe',
    ).add_to(map)
    st_data = st_folium(map)


# melk per koe
with map_milk_per_cow:
    map2 = folium.Map(location=[48, 12], zoom_start=4, tiles='cartodbpositron')
    folium.Choropleth(
        geo_data='countries.geojson',
        data=filtered_mapdf,
        columns=['country_ISO3', 'milk_per_cow'],
        key_on='properties.ISO_A3',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Milk per cow in Europe',
    ).add_to(map2)
    st_data = st_folium(map2)

st.divider()

prediction_fig, prediction_info = st.columns(2)


#lineair model bouwen en voorspellen
filtered_data = filtered_data.dropna(axis=0)
country_encoding = {
    'AT': 1, 'BE': 2, 'BG': 3, 'CH': 4, 'CY': 5, 'CZ': 6, 'DE': 7, 'DK': 8, 'EE': 9, 'EL': 10,
    'ES': 11, 'FI': 12, 'FR': 13, 'HR': 14, 'HU': 15, 'IE': 16, 'IT': 17, 'LT': 18, 'LU': 19, 'LV': 20,
    'ME': 21, 'MK': 22, 'MT': 23, 'NL': 24, 'PL': 25, 'PT': 26, 'RO': 27, 'RS': 28, 'SE': 29, 'SI': 30,
    'SK': 31, 'UK': 32, 'XK': 33
}

# str naar int door encoding
filtered_data['country'] = filtered_data['country'].map(country_encoding)
filtered_data['year'] = filtered_data['year'].dt.year.astype('int32')
Y = filtered_data['milk_production']
X = filtered_data[['year', 'country','cows']]

X = sm.add_constant(X)  
model = sm.OLS(Y, X).fit()
predictions = model.predict(X) 
filtered_data['predictions'] = predictions
reverse_country_encoding = {v: k for k, v in country_encoding.items()}
filtered_data['country'] = filtered_data['country'].map(reverse_country_encoding)

# Voorspel df maken
years = list(range(2023, 2049))  # Jaren van 2023 tot 2048
countries = filtered_data['country'].unique()
year_country_combinations = [(year, country) for year in years for country in countries]
voorspel_df = pd.DataFrame(year_country_combinations, columns=['year', 'country'])
voorspel_df['cows'] = voorspel_df['country'].map(filtered_data.groupby('country')['cows'].mean())
voorspel_df['country'] = voorspel_df['country'].map(country_encoding)


# Voorspellingen 
voorspel_df = sm.add_constant(voorspel_df) 
predicted_values = model.predict(voorspel_df)
voorspel_df['predicted_milk_production'] = predicted_values
reverse_country_encoding = {v: k for k, v in country_encoding.items()}
voorspel_df['country'] = voorspel_df['country'].map(reverse_country_encoding)


with prediction_fig:   
    fig = px.line(voorspel_df, markers = True,
                  x="year", y='predicted_milk_production', 
                  title='Aantal lter melk per jaar',
                  color = 'country')
    fig.update_xaxes(title_text='Jaar')
    fig.update_yaxes(title_text='Aantal liter melk')
    st.plotly_chart(fig)
with prediction_info:
    '''
    # Hoe ziet de toekomst eruit? :crystal_ball:
    
    De toekomst van melkproductie in Europa is een onderwerp van groot belang, zowel vanuit economisch oogpunt als vanuit het perspectief van duurzaamheid en milieubescherming. De voorspelling van melkproductie is van essentieel belang voor boeren, beleidsmakers en de zuivelsector als geheel. Een veelgebruikte methode voor het voorspellen van melkproductie is het gebruik van lineaire regressiemodellen, die historische gegevens en trends analyseren om toekomstige productie te schatten.

    In Europa speelt de melkproductie een cruciale rol in de agrarische sector. Het continent herbergt verschillende landen met grote zuivelsectoren en heeft een lange geschiedenis in de melkveehouderij. Echter, de toekomst van de melkproductie wordt beïnvloed door verschillende factoren, waaronder marktvraag, beleidsmaatregelen, technologische ontwikkelingen en milieukwesties.

    Een lineair regressiemodel kan historische gegevens over melkproductie in Europa gebruiken om toekomstige trends te voorspellen. Het gebruik van gegevens en modellen kan boeren en beleidsmakers helpen bij het plannen van de toekomstige ontwikkelingen in de melkproductie, met aandacht voor zowel economische groei als milieubehoud.
    
    '''


