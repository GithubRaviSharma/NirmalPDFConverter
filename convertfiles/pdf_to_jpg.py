import streamlit as st
from pdf2image import convert_from_path
import tempfile
import datetime
from PIL import Image
import io
import socket
import os
import pyodbc

st.set_page_config(
        page_title="निर्मल: PDF to JPG ",
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


# Function to check if a file is a valid PDF file
def is_pdf(file):
    # PDF magic number (header)
    pdf_magic_number = b'%PDF'

    # Read the first 4 bytes of the file
    first_bytes = file.read(4)
    file.seek(0)  # Reset file pointer to beginning

    # Check if the file header matches the PDF magic number
    return first_bytes.startswith(pdf_magic_number)

# Function to convert PDF to JPG
def convert_pdf_to_jpg(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_file.read())
        temp_pdf_path = temp_pdf.name

    images = convert_from_path(temp_pdf_path, poppler_path=r'C:\Program Files (x86)\poppler-24.02.0\Library\bin')
    jpg_images = []
    for i, image in enumerate(images):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        jpg_images.append((f"page_{i + 1}.jpg", img_byte_arr))
    return jpg_images

# Get the current year dynamically
def get_current_year():
    return datetime.datetime.now().year

# Define the Streamlit app function
def app():
    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return

    st.markdown("<h1 style='text-align: center;'><  निर्मल: PDF to JPG Converter  ></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the second column
    with col1:
        st.image('./Images/pdf-to-jpg.webp', width=705)

    # File uploader for PDF files
    uploaded_file = st.file_uploader("*Upload a PDF file containing images that you want to convert.", type=["pdf"])

    if uploaded_file is not None:
        file_size = len(uploaded_file.getvalue())
        
        if is_pdf(uploaded_file):
            st.success("PDF file uploaded successfully!")
            if st.button("Convert to JPG"):
                st.info("Download the Converted JPG File(s)")
                try:
                    jpg_files = convert_pdf_to_jpg(uploaded_file)

                    # Provide download links for the converted JPG files
                    for filename, jpg in jpg_files:
                        st.download_button(
                            label=f"Download {filename}",
                            data=jpg,
                            file_name=filename,
                            mime="image/jpeg"
                        )
 
                except Exception as e:
                    st.error(f"Error converting PDF to JPG: {e}")
        else:
            st.warning("Please upload a valid PDF file.")

        insert_file_data(
                name=uploaded_file.name,
                description = "PDF to JPG",
                status=1,  # Example status
                content_type=os.path.splitext(uploaded_file.name)[1].lower(),  # Get file extension
                size=file_size,
                updated_by= st.session_state.username ,  # Get current user's login name
                updated_on=datetime.datetime.now(),  # Current date and time
                updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
        )

# Run the Streamlit app
if __name__ == "__page__":
    app()
