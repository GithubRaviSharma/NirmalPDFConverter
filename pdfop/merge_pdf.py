import streamlit as st
import tempfile
import os
from PyPDF2 import PdfReader, PdfWriter
import datetime
import pyodbc
import socket

st.set_page_config(
    page_title="निर्मल: PDF Merger",
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

# Function to insert file data using a stored procedure and get BlockId
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

            # Display success message (optional)
            # st.success(f"File log updated successfully!.")
          
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

# Function to merge PDFs
def merge_pdfs(pdf_files):
    pdf_writer = PdfWriter()
    for pdf_file in pdf_files:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    merged_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(merged_pdf_file, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    return merged_pdf_file

# Function to check if a file is a PDF
def is_pdf(file):
    # Define PDF magic number (header)
    pdf_magic_number = b"%PDF"

    # Read the first 4 bytes of the file
    first_bytes = file.read(4)

    # Reset file pointer to the beginning
    file.seek(0)

    # Check if the file header matches the PDF magic number
    return first_bytes == pdf_magic_number

# App function to encapsulate Streamlit logic
def app():
    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return

    st.markdown("<h1 style='text-align: center;'><  निर्मल: Multiple PDF's Merger  ></h1>", unsafe_allow_html=True)
    st.image('./Images/merge-pdf-color.webp', width=550)

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

    # File uploader for PDF files
    uploaded_files = st.file_uploader("*Upload multiple PDF files to merge.", type="pdf", accept_multiple_files=True, key="multipdf_uploader")

    if uploaded_files:
        st.success("PDF Files uploaded Successfully!")
        pdf_files = []
        current_time = datetime.datetime.now().replace(microsecond=0)
        
        for uploaded_file in uploaded_files:
            if is_pdf(uploaded_file):
                file_size = len(uploaded_file.getvalue())

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(uploaded_file.getbuffer())
                    pdf_files.append(temp_pdf.name)

            else:
                st.warning("Please Upload a valid PDF File.")

        if pdf_files:
            # Insert file data into the database once for all valid PDFs
            for pdf_file in pdf_files:
                insert_file_data(
                    name=os.path.basename(pdf_file),
                    description="Merging PDF",
                    status=1,  # Example status
                    content_type=".pdf",  # Assuming all are PDFs
                    size=os.path.getsize(pdf_file),
                    updated_by=st.session_state.username,  # Get current user's login name
                    updated_on=current_time,  # Current date and time
                    updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
                )

            # Merge PDFs
            merged_pdf_file = merge_pdfs(pdf_files)

            # Provide download link for the merged PDF file
            with open(merged_pdf_file, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(
                    label="Download Merged PDF",
                    data=pdf_bytes,
                    file_name="merged.pdf",
                    mime="application/pdf"
                )

            # Clean up temporary files
            for pdf_file in pdf_files:
                os.remove(pdf_file)
            os.remove(merged_pdf_file)

# Main application logic
if __name__ == "__page__":
    app()
