import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pyodbc
import datetime

#######################
# Set Streamlit page configuration
st.set_page_config(
    page_title="निर्मल: Dashboard",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

st.logo("Images/powergrid.webp")


# Sidebar logo and footer
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
    """, 
    unsafe_allow_html=True
)

# Get the current year
def get_current_year():
    return datetime.datetime.now().year

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

# Function to get total logins (hit count)
def get_total_logins():
    conn = connect_to_db()
    query = "EXEC GetTotalLogins"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['TotalLogins'][0]

# Function to calculate total data size in GB
def calculate_total_size_gb():
    df = load_data()
    total_bytes = df['Size'].sum()
    total_gb = total_bytes / (1024 ** 3)  # Convert bytes to GB
    return total_gb

def make_bar_chart(input_df):
    input_df['UpdatedOn'] = pd.to_datetime(input_df['UpdatedOn'])  # Ensure 'UpdatedOn' is datetime format
    
    last_30_days = pd.Timestamp.today() - pd.Timedelta(days=30)
    recent_df = input_df[input_df['UpdatedOn'] >= last_30_days]
    recent_df['DateOnly'] = recent_df['UpdatedOn'].dt.date  # Keep only the date part
    grouped_by_date = recent_df.groupby('DateOnly').size().reset_index(name='FileCount')
    
    fig = px.bar(grouped_by_date, x='DateOnly', y='FileCount')
    
    fig.update_layout(
        title={
            'text': 'Conversions in the Last 30 Days',
            'x': 0.35,  # Center title horizontally
            'y': 0.95  # Adjust title position vertically if needed
        },
        xaxis_title='Date',
        yaxis_title='File Count',
        template='plotly_dark',  # Dark theme for the chart
        xaxis=dict(
            type='category'  # Use category type for dates to avoid time labels
        )
    )
    
    return fig



with st.sidebar:
    st.image('./Images/logo-white.png', width=150)
    st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {get_current_year()} All rights reserved.</h6>""", unsafe_allow_html=True)

# Load data
def load_data():
    conn = connect_to_db()
    query = "EXEC GetFilesData"
    df = pd.read_sql(query, conn)
    df['year'] = pd.to_datetime(df['UpdatedOn']).dt.year
    df['month'] = pd.to_datetime(df['UpdatedOn']).dt.month_name()
    conn.close()
    return df

# Function to load data from UserLogIn
def load_data_User():
    conn = connect_to_db()
    query = "EXEC GetUserLogInData"
    dff = pd.read_sql(query, conn)
    dff['year'] = pd.to_datetime(dff['LoggedIn']).dt.year
    dff['month'] = pd.to_datetime(dff['LoggedIn']).dt.month_name()
    conn.close()
    return dff

# Main function
def app():
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.error("🔒 Please log in before accessing the resource.")
        return

    df = load_data()
    dff = load_data_User()
    
    # Dashboard Main Panel
    col = st.columns((1.5, 4.5, 2), gap='medium')

    with col[0]:
        st.write("")
        if df is not None:
            # Total logins (hit count)
            hit_count = get_total_logins()
            st.markdown(
                f"""
                <div style='
                    background-color: #DC143C; 
                    border-radius: 5px; 
                    padding: 10px; 
                    text-align: center;
                    box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);'>
                    <p style='margin: 0;font-size: 27px; font-weight: bold; color: white;'>Hit Count</p>
                    <p style='margin: 0; font-size: 20px; font-weight: bold; color: white;'>{hit_count}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")
            st.write("")

            # Total files uploaded
            total_files = len(df)
            st.markdown(
                f"""
                <div style='
                    background-color: #FF6347; 
                    border-radius: 5px; 
                    padding: 10px; 
                    text-align: center;
                    box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);'>
                    <p style='margin: 0; font-size: 27px; font-weight: bold; color: white;'>Conversions</p>
                    <p style='margin: 0; font-size: 20px; font-weight: bold; color: white;'>{total_files}</p>
                </div>
                """,                          
            unsafe_allow_html=True
            )
            st.write("")
            st.write("")

            df['UpdatedBy'] = df['UpdatedBy'].str.strip()

            # Total unique users
            total_users = df['UpdatedBy'].nunique()
            st.markdown(
                f"""
                <div style='
                    background-color: #5733FF; 
                    border-radius: 5px; 
                    padding: 10px; 
                    text-align: center;
                    box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);'>
                    <p style='margin: 0;font-size: 27px; font-weight: bold; color: white;'>Total Users</p>
                    <p style='margin: 0; font-size: 20px; font-weight: bold; color: white;'>{total_users}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")
            st.write("")


            # Display total data size in GB
            total_size_gb = calculate_total_size_gb()
            st.markdown(
                f"""
                <div style='
                    background-color: #D2691E; 
                    border-radius: 5px; 
                    padding: 10px; 
                    text-align: center;
                    box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);'>
                    <p style='margin: 0; font-size: 27px; font-weight: bold;color: white;'> Data prcd</p>
                    <p style='margin: 0; font-size: 20px; font-weight: bold; color: white;'>{total_size_gb:.2f} GB</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("")
            st.write("")

        else:
            st.error("Failed to load data")
                          
    with col[1]:
        st.markdown(f"""<h1 style='text-align: center;'>< निर्मल: User's Dashboard ></h1>""", unsafe_allow_html=True) 
        st.plotly_chart(make_bar_chart(df))
    
    with col[2]:
        st.markdown(f"""<h6 style='text-align: center;'>User Leaderboard</h6>""", unsafe_allow_html=True)
        
        # Group by EmpName and aggregate to get hit count and most recent hit
        grouped_users = dff.groupby('EmpName').agg(
            HitCount=('ID', 'count'),
            MostRecentHit=('LoggedIn', 'max')
        ).reset_index()
        
        # Sort by HitCount in descending order
        sorted_users = grouped_users.sort_values(by='HitCount', ascending=False)
        
        # Ensure top 5 unique users
        top_users = sorted_users.drop_duplicates(subset=['EmpName']).head(5)
        
        # Ensure exactly 5 users are displayed (if less than 5 unique users, fill with NaN)
        if len(top_users) < 5:
            missing_users_count = 5 - len(top_users)
            missing_users_df = pd.DataFrame({'EmpName': [''] * missing_users_count})
            top_users = pd.concat([top_users, missing_users_df]).reset_index(drop=True)
        
        # Rename columns for display
        top_users.columns = ['Employee Name', 'Hit Count', 'Most Recent Hit']
    
    # Display leaderboard
        st.dataframe(top_users, hide_index=True)


            
        with st.expander('About', expanded=True):
                st.write('''
                    - Data Source: Powergrid Database.
                    - Displays the total number of files uploaded and unique users.
                    - Visualizes the trend of file uploads over time.
                    - Lists the top 5 users by the number of uploads.
                    ''')
            
    if df is not None:
        description_counts = df['Description'].value_counts().reset_index()
        description_counts.columns = ['Description', 'Count']

        # Define a list of colors for boxes
        box_colors = ['#FF5733', '#4682B4', '#5733FF', '#00BFA6', '#FF69B4', '#DC143C', '#9400D3', '#7B68EE','#D2691E','#4B0082','#CD5C5C','#1E90FF']  # Add more colors as needed
        
        # Title position adjustments
        title_style = """
            text-align: center;
            margin-top: -58px;  /* Adjust vertical position */
            margin-bottom: -200px; 
            """
        
        st.write("")
        st.write("")
        st.markdown(f"""<h3 style="{title_style}">< File Conversion Count ></h3>""", unsafe_allow_html=True)
        st.write("")

        # Create rows of four columns each
        for row in range(0, len(description_counts), 4):
            cols = st.columns(4)
            for i in range(4):
                index = row + i
                if index < len(description_counts):
                    color_index = index % len(box_colors)
                    box_style = f"""
                        display: flex; 
                        flex-direction: column; 
                        justify-content: center; 
                        align-items: center; 
                        padding: 20px; 
                        border-radius: 10px; 
                        background-color: {box_colors[color_index]}; 
                        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        height: 100px;
                        margin: 10px 0;  /* Reduced margin to adjust spacing */
                    """
                    with cols[i]:
                        st.markdown(f"""
                            <div style="{box_style}">
                                <h4 style="margin: 0;font-size: 27px; font-weight: bold; color: white;">{description_counts.iloc[index]['Description']}</h4>
                                <p style="margin: 0; font-size: 24px; font-weight: bold; color: white;">{description_counts.iloc[index]['Count']}</p>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.error("Failed to load data") 
        
    st.write("") 
    st.write("")
    st.write("")  

    
    footer = """
        <style>
        .main-footer {
            font-size: 12px;
            color: gray;
            text-align: center; 
            bottom: 0;
            width: 100%;
        }
        </style>
        <div class="main-footer">
            <h6 style='text-align: center;'>Powergrid Corporation of India &copy; """ + str(get_current_year()) + """ All rights reserved.</h6>
        </div>
        """
    st.markdown(footer, unsafe_allow_html=True)

if __name__ == "__page__":
    app()
