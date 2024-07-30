import streamlit as st
import pyodbc
import datetime
import socket

# Function to get current year
def get_current_year():
    return datetime.datetime.now().year

st.set_page_config(
    page_title="निर्मल : Login",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="collapsed"
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
        st.write("")
        st.image('./Images/logo-white.png', width=150)

with st.sidebar:
        st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {datetime.datetime.now().year} All rights reserved.</h6>""", unsafe_allow_html=True)

# Initialize session state for authentication status
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Function to connect to the database
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

# Function to check user credentials
def check_credentials(username, password):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("{CALL sp_AuthenticateUser (?)}", username)
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_password = result[0]
        return stored_password == password
    return False

# Function to parse user agent information
# def get_user_agent():
#     return user_agents.parse("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Function to log user login
def log_user_login(emp_name, user_host_address, user_host_name, logged_in):
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("{CALL sp_InsertUserLogIn (?, ?, ?, ?)}",
                           emp_name, user_host_address, user_host_name, logged_in)
            conn.commit()
    except pyodbc.Error as e:
        st.error(f"Error logging user login: {e}")
    except Exception as ex:
        st.error(f"Unexpected error: {ex}")
    finally:
        if conn:
            conn.close()

# Main login and authentication UI
st.write("""<h1 style='text-align: center;'>< निर्मल : Login & Authentication ></h1>""", unsafe_allow_html=True)
st.image('Images/powergrid.webp', width=650)

# Streamlit app for user login
if not st.session_state.authenticated:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username.strip() == "" or password.strip() == "":
            st.warning("Please enter both username and password.")
        else:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                log_user_login(
                    emp_name=username,
                    user_host_address=socket.gethostbyname(socket.gethostname()),  # Example of retrieving IP address
                    user_host_name=socket.gethostname(),  # Example of retrieving hostname
                    logged_in=datetime.datetime.now()  # Current date and time
                )           
                st.experimental_rerun()  # Refresh the page after login
            else:
                st.error("Invalid username or password.")
else:
    st.info("You are logged in!")
    # If authenticated, show logout button
    col1, col2, col3     = st.columns(3)
    with col1:
        if st.button("Logout <🌐> "):
            st.session_state.authenticated = False
            st.success("Logout successful.")
            st.experimental_rerun()  # Refresh the page after logout
    
    # Button to download user manual
    with col3:
        with open("User Manual - Nirmal.pdf", "rb") as file:
            st.download_button(
                label="Download User Manual <📖>",
                data=file,
                file_name="Nirmal - User Manual.pdf",
                mime="application/pdf"
            )
