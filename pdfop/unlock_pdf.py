import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import datetime
import socket
import os
import pyodbc

# Set the page configuration first
st.set_page_config(
    page_title="निर्मल: Unlock PDF",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.logo("Images/powergrid.webp")

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

with st.sidebar:
  def get_current_year():
    return datetime.datetime.now().year

  with st.sidebar:
    st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {get_current_year()} All rights reserved.</h6>""", unsafe_allow_html=True)    

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

# Function to insert file data using a stored procedure
def insert_file_data(name, description, status, content_type, size, updated_by, updated_on, updated_from):
    try:
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()

            # Convert Python types to SQL Server expected types
            updated_on_sql = updated_on.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if isinstance(updated_on, datetime.datetime) else updated_on
            size = int(size)  # Convert size to integer
            status = int(status)  # Convert status to integer

            # Call the stored procedure with parameters in correct order
            cursor.execute("{CALL sp_InsertFile ( ?, ?, ?, ?, ?, ?, ?, ?)}",
                           (name, description, status, content_type, size, updated_by, updated_on_sql, updated_from))

            conn.commit()
            # st.info("File logged successfully!")
    except pyodbc.Error as e:
        st.error(f"Error inserting file data: {e}")
        # More detailed error logging
        st.write("SQL Error:", e)
        st.write("SQL State:", e.args[0])
        st.write("SQL Message:", e.args[1])
    except Exception as ex:
        st.error(f"Unexpected error: {ex}")
    finally:
        if conn:
            conn.close()

# Function to check if a file is a valid PDF (magic number check)
def is_valid_pdf(file):
    file.seek(0)  # Ensure we are at the beginning of the file
    header = file.read(4)  # Read the first 4 bytes
    file.seek(0)  # Reset file pointer to beginning
    return header == b'%PDF'

# Function to unlock a protected PDF with the correct password
def unlock_pdf(uploaded_file, password):
    reader = PdfReader(uploaded_file)
    
    if reader.is_encrypted:
        reader.decrypt(password)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        output_pdf = BytesIO()
        writer.write(output_pdf)
        output_pdf.seek(0)
        
        return output_pdf
    else:
        return None

def app():
    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return
    
    st.markdown("<h1 style='text-align: center;'><  निर्मल: PDF Password Unlocker  ></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the second column
    with col1:
        st.image('./Images/unlockpdfsv.png', width=580)
    uploaded_file = st.file_uploader("*Upload a PDF file that you want to unlock.", type="pdf", key="unlock_uploader")

    if uploaded_file is not None:
        if is_valid_pdf(uploaded_file):
            file_size = len(uploaded_file.getvalue())
            st.success("PDF uploaded successfully!")
            insert_file_data(
                name=uploaded_file.name,
                description="Unlocking PDF",
                status=1,  # Example status
                content_type=os.path.splitext(uploaded_file.name)[1].lower(),  # Get file extension
                size=file_size,
                updated_by=st.session_state.username,  # Get current user's login name
                updated_on=datetime.datetime.now(),  # Current date and time
                updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
            )
        else:
            st.warning("Please upload a valid PDF file.")
            return
    
        
        password = st.text_input("Enter password for the PDF:", type="password")
        
        if st.button("Unlock PDF"):
            if password:
                unlocked_pdf = unlock_pdf(uploaded_file, password)
                if unlocked_pdf:
                    st.success("PDF unlocked successfully!")
                    st.download_button(label="Download Unlocked PDF", data=unlocked_pdf.getvalue(), file_name="unlocked.pdf")
                else:
                    st.error("Incorrect password or unable to unlock PDF.")
            else:
                st.warning("Please enter the password to unlock the PDF.")

if __name__ == "__page__":
    app()
