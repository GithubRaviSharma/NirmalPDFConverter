import streamlit as st
import pandas as pd
import pyodbc
import datetime

#######################
# Set Streamlit page configuration
st.set_page_config(
    page_title="निर्मल: MIS",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.image('./Images/logo-white.png', width=150)
def get_current_year():
    return datetime.datetime.now().year

with st.sidebar:
    st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {get_current_year()} All rights reserved.</h6>""", unsafe_allow_html=True) 

# Get the current year
def get_current_year():
    return datetime.datetime.now().year

st.logo("Images/powergrid.webp")


# Database connection
def connect_to_db():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=Z3PHYR\\SQLEXPRESS;"
        "Database=PowergridDB;"
        "UID=sa;"
        "PWD=powergrid;"
        "Encrypt=no;"
    )
    return conn

def load_data():
    conn = connect_to_db()
    query = "EXEC GetFilesData"
    df = pd.read_sql(query, conn)
    df['UpdatedOn'] = pd.to_datetime(df['UpdatedOn'])
    conn.close()
    return df

def load_data_dff():
    conn = connect_to_db()
    query = "EXEC GetUserLogIn"
    dff = pd.read_sql(query, conn)
    dff['LoggedIn'] = pd.to_datetime(dff['LoggedIn'])
    conn.close()
    return dff

# Main function
def app():
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.error("🔒 Please log in before accessing the resource.")
        return
    
    st.markdown(f"""<h1 style='text-align: center;'>< निर्मल: Management Information System ></h1>""", unsafe_allow_html=True)
    st.write("")

    left_co, cent_co,last_co = st.columns(3)
    with cent_co:
        st.image("Images/powergrid.webp")
    
    st.write("")
    st.write("")


    
    # Load the data
    df = load_data()
    dff = load_data_dff()
    
    # Date range filter
    col0, col1, col2, col3 = st.columns([2, 6, 1, 1])
    
    with col1:
       st.markdown(f"""<h4 style='text-align: center;'>< File Meta Data ></h4>""", unsafe_allow_html=True)
       min_date = df['UpdatedOn'].min().date()
       max_date = df['UpdatedOn'].max().date()
       st.write("")
       start_date, end_date = st.date_input('*Select date range:', [min_date, max_date], min_value=min_date, max_value=max_date)
       
       if start_date and end_date:
           filtered_df = df[(df['UpdatedOn'].dt.date >= start_date) & (df['UpdatedOn'].dt.date <= end_date)]
       else:
           filtered_df = df
       
       st.dataframe(filtered_df)

    st.write("")
    st.write("")

    col0, col1, col2, col3 = st.columns([2, 3, 1, 1])
    
    with col1:
       st.markdown(f"""<h4 style='text-align: center;'>< User LogIn Data ></h4>""", unsafe_allow_html=True)
       # Date range filter for UserLogIn data
       min_date_dff = dff['LoggedIn'].min().date()
       max_date_dff = dff['LoggedIn'].max().date()
       st.write("")
       st.write("")
       start_date_dff, end_date_dff = st.date_input('*Select date range for UserLogIn data:', [min_date_dff, max_date_dff], min_value=min_date_dff, max_value=max_date_dff)
       
       if start_date_dff and end_date_dff:
           filtered_dff = dff[(dff['LoggedIn'].dt.date >= start_date_dff) & (dff['LoggedIn'].dt.date <= end_date_dff)]
       else:
           filtered_dff = dff



       # Display the UserLogIn data
       st.dataframe(filtered_dff)
       


    st.write("")
    st.write("")

if __name__ == "__page__":
    app()
