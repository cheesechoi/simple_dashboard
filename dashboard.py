# streamlit run dashboard.py

import streamlit as st
import plotly.express as px
import pandas as pd 

# Set page title
st.set_page_config(page_title="My Streamlit App", page_icon=":shark:", layout="wide")

# Add title and text to page
st.title(" :bar_chart: Welcome to my Streamlit app! really")
st.write("This is some sample text.")

st.markdown("## :chart_with_upwards_trend: Plotting a DataFrame")
#st.markdown('<style>h1{color: red;}</style>', unsafe_allow_html=True)
st.markdown('<style>div.block-container{patting-top:1rem;}</style>', unsafe_allow_html=True)


fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "xls", ])

if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(fl)
else:
    df = pd.read_excel("Superstore.xls")#, encoding="ISO-8859-1")


col1, col2 = st.columns(2)
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Getting the min and max date from the dataframe
startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End date", endDate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

st.sidebar.header(" :bar_chart: Choose your filter: ")
region = st.sidebar.multiselect("Region", df['Region'].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)].copy()

# Create for State
state = st.sidebar.multiselect("Pick the State", df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)].copy()

# Create for City
city = st.sidebar.multiselect("Pick the City", df3['City'].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3['City'].isin(city)].copy()

# Filter the data based on Region, State and City

filtered_df = df4.copy()

#category_df = filtered_df.groupby(by = ['Category'])["Sales"].sum()
category_df = filtered_df.groupby(by = ['Category'], as_index = False)["Sales"].sum()

with col1:
    st.subheader(" :bar_chart: Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales",
           text = [f'${x:,.2f}' for x in category_df['Sales']],
           template = "seaborn")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(" :bar_chart: Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
        #    title = "Sales by Region",
        #    template = "seaborn")
    fig.update_traces(text = filtered_df['Region'], textposition = "outside", textinfo = "percent+label")
    st.plotly_chart(fig, use_container_width=True)


cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button(
            label = "Download CSV",
            data = csv,
            file_name = "Category.csv",
            mime = "text/csv",
            help = 'Click to download the above CSV file'
        )
with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby(by = ['Region'], as_index = False)["Sales"].sum()
        st.write(region_df.style.background_gradient(cmap = "Oranges"))
        csv = region_df.to_csv(index = False).encode('utf-8')
        st.download_button(
            label = "Download CSV",
            data = csv,
            file_name = "Region.csv",
            mime = "text/csv",
            help = 'Click to download the above CSV file'
        )


filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')
st.subheader(" :bar_chart: Time Series Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales": "Amount"}, height = 500, width = 1000, template = "gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap = "Greens"))
    csv = linechart.to_csv(index = False).encode('utf-8')
    st.download_button(
        label = "Download CSV",
        data = csv,
        file_name = "TimeSeries.csv",
        mime = "text/csv",
        help = 'Click to download the above CSV file'
    )

st.subheader("Hierarchial view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ['Region', 'Category', 'Sub-Category'], values = 'Sales',
                  hover_data = ["Sales"], color = "Sub-Category", color_discrete_sequence = px.colors.qualitative.Prism)
fig3.update_layout(width = 800, height= 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader(" :bar_chart: Segment wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text=filtered_df['Segment'], textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    st.subheader(" :bar_chart: Category wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text=filtered_df['Category'], textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):

    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Sub-Catgory Table")
    filtered_df['month'] = filtered_df['Order Date'].dt.to_period('M')
    sub_category_year = pd.pivot_table(data = filtered_df, values= "Sales", index = ["Sub-Category"], columns = "month")
    st.write(sub_category_year.style.background_gradient(cmap = "Blues"))

data1 = px.scatter(filtered_df, x = "Sales", y = "Profit",
                    size = "Quantity")
data1['layout'].update(title="Relationship beetwen Sales, Profit",
                       titlefont = dict(size=20), xaxis = dict(title = "Sales", titlefont = dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap = "Oranges"))

# Download original dataset
csv = df.to_csv(index = False).encode('utf-8')
st.download_button(
    'Download Data', data = csv, file_name = 'Data.csv', mime = 'text/csv')