import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

# Load and process data
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('clean_powertrust_data.csv')
    df['SMRStartDt'] = pd.to_datetime(df['SMRStartDt'])
    df['SMREndDt'] = pd.to_datetime(df['SMREndDt'])
    df['Month'] = df['SMRStartDt'].dt.month_name()
    df['Year'] = df['SMRStartDt'].dt.year
    return df

df = load_and_process_data()

st.title('Powertrust Dashboard')

# Sidebar for plot selection
st.sidebar.header('Plot Selection')
selected_plot = st.sidebar.selectbox(
    'Choose a plot to display',
    ['Value (KWh) by Country',
     'Value (KWh) by Developer',
     'Energy Distribution by Developer in Month ',
     'Monthly Value (KWh) Energy Generation',
     'Energy Generation by Certification Status']
)

# Sidebar filters
st.sidebar.header('Filters')
countries = st.sidebar.multiselect('Select Countries', df['Country'].unique())
developers = st.sidebar.multiselect('Select Developers', df['DevName'].unique())
years = st.sidebar.multiselect('Select Years', sorted(df['Year'].unique()))

# Apply filters
filtered_df = df
if countries:
    filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
if developers:
    filtered_df = filtered_df[filtered_df['DevName'].isin(developers)]
if years:
    filtered_df = filtered_df[filtered_df['Year'].isin(years)]



# KPI metrics
total_value_kwh = filtered_df['Value (KWh)'].sum()
avg_value_kwh = filtered_df['Value (KWh)'].mean()
num_projects = filtered_df['SiteId'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Value (KWh)", f"{total_value_kwh:,.2f}")
col2.metric("Average Value (KWh)", f"{avg_value_kwh:,.2f}")
col3.metric("Number of Projects", num_projects)



# Map: Value (KWh) by Country
#st.subheader('Value (KWh) Energy Generation by Country')
map_data = filtered_df.groupby('Country')[['Value (KWh)']].sum().reset_index()
fig_map = px.choropleth(map_data, locations='Country', locationmode='country names',
                        color='Value (KWh)', hover_name='Country',
                        color_continuous_scale='blues')
#st.plotly_chart(fig_map)

# Bar Plot: Value (KWh) by Developer
#st.subheader('Value (KWh) Energy Generation by Developer')
fig_bar = px.bar(filtered_df.groupby('DevName')[['Value (KWh)']].sum().reset_index(),
                 x='DevName', y='Value (KWh)', color='Value (KWh)')
#st.plotly_chart(fig_bar)

# Heatmap: Value (KWh) by Month and Developer
#st.subheader('Value (KWh) Energy Distribution by Month and Developer')
heatmap_data = filtered_df.groupby(['Month', 'DevName'])['Value (KWh)'].sum().unstack().fillna(0)
heatmap_data = heatmap_data.reindex(calendar.month_name[1:])
fig_heatmap = px.imshow(heatmap_data, labels=dict(x="Developer", y="Month", color="Value(KWh)"),
                        x=heatmap_data.columns, y=heatmap_data.index)
#st.plotly_chart(fig_heatmap)

# Line Plot: Monthly Value (KWh) Generation
#st.subheader('Monthly Value (KWh) Energy Generation')
monthly_data = filtered_df.groupby(['Year', 'Month'])['Value (KWh)'].sum().reset_index()
monthly_data['MonthIndex'] = monthly_data['Month'].apply(lambda x: list(calendar.month_name).index(x))
monthly_data = monthly_data.sort_values(by=['Year', 'MonthIndex'])
monthly_data['YearMonth'] = monthly_data['Year'].astype(str) + '-' + monthly_data['Month']
fig_line = px.line(monthly_data, x='YearMonth', y='Value (KWh)', markers=True)
#st.plotly_chart(fig_line)

# Scatter Plot: Value (KWh) vs Capacity (KW) by Certification Status
#st.subheader('Energy Generation Value (KWh) vs Capacity (KW) by Certification Status of Solar Devices')
fig_scatter = px.scatter(filtered_df, x='Capacity (KW)', y='Value (KWh)',
                         color='IsCertified', hover_data=['DevName'])
#st.plotly_chart(fig_scatter)


# Plot generation based on selection
if selected_plot == 'Value (KWh) by Country':
    st.subheader('Value (KWh) Energy Generation by Country')
    st.plotly_chart(fig_map)

elif selected_plot == 'Value (KWh) by Developer':
    st.subheader('Value (KWh) Energy Generation by Developer')
    st.plotly_chart(fig_bar)

elif selected_plot == 'Energy Distribution by Developer in Month ':
    st.subheader('Value (KWh) Energy Distribution by Month and Developer')
    st.plotly_chart(fig_heatmap)

elif selected_plot == 'Monthly Value (KWh) Energy Generation':
    st.subheader('Monthly Value (KWh) Energy Generation')
    st.plotly_chart(fig_line)

elif selected_plot == 'Energy Generation by Certification Status':
    st.subheader('Energy Generation Value (KWh) vs Capacity (KW) by Certification Status of Solar Devices')
    st.plotly_chart(fig_scatter)

# Display raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)



