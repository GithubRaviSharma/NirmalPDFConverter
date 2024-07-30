import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import datetime
import pyodbc
import socket
import os

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

st.logo("Images/powergrid.webp")


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

# Function to extract PDF pages by page numbers
def extract_pdf_pages(input_pdf, page_numbers):
    pdf_reader = PdfReader(input_pdf)
    extracted_pages = []

    for page_num in page_numbers:
        if 1 <= page_num <= len(pdf_reader.pages):
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num - 1])  # Page numbers are 0-based in PyPDF2, so adjust accordingly

            # Save to a bytes buffer
            pdf_buffer = io.BytesIO()
            pdf_writer.write(pdf_buffer)
            pdf_buffer.seek(0)
            extracted_pages.append((f'Page_{page_num}.pdf', pdf_buffer))
        else:
            st.warning(f"Page number {page_num} is out of range.")

    return extracted_pages

# Function to check if the file is a PDF using magic number
def is_pdf(file):
    file.seek(0)
    magic_number = file.read(4)
    file.seek(0)  # Reset file pointer to the beginning
    return magic_number == b'%PDF'

# Main Streamlit app
def app():
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="निर्मल: PDF Extractor",
        page_icon="🔄",
        layout="centered",
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

    with st.sidebar:
        st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {datetime.datetime.now().year} All rights reserved.</h6>""", unsafe_allow_html=True)

    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return
    
    st.markdown("<h1 style='text-align: center;'><  निर्मल: PDF Page Extractor ></h1>", unsafe_allow_html=True)
    # Layout setup
   # Layout setup
    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the second column
    with col2:
        st.image('./Images/how-to-extract-pdf.png', width=460)   
    st.write("")
    
    uploaded_file = st.file_uploader("*Upload a PDF file from which you want to extract pages.", type="pdf", key="extract_uploader")

    # Initialize extracted pages list in session state if it doesn't exist
    if 'extracted_pages' not in st.session_state:
        st.session_state.extracted_pages = []

    if uploaded_file:
        if is_pdf(uploaded_file):
            st.success("PDF File uploaded successfully!")
            file_size = len(uploaded_file.getvalue())
            pdf_reader = PdfReader(uploaded_file)
            total_pages = len(pdf_reader.pages)
            st.write("")
            st.markdown(f"""<h6 style='text-align: center;'>The uploaded PDF has {total_pages} pages.""", unsafe_allow_html=True)
            st.write("")

            # Get the specific page numbers to extract
            page_numbers = st.text_input("*Enter page numbers to extract (comma-separated).", key="page_numbers")

            if st.button("Extract Pages"):
                if page_numbers:
                    # Convert page_numbers to a list of integers
                    try:
                        page_numbers = [int(num.strip()) for num in page_numbers.split(',')]
                    except ValueError:
                        st.warning("Please enter valid page numbers.")
                        return

                    if page_numbers:
                        # Extract pages and update session state
                        st.session_state.extracted_pages = extract_pdf_pages(uploaded_file, page_numbers)

                        # st.success("Pages were Successfully extracted from the PDF!")
                        st.write("")
                        st.markdown(f"""<h6 style='text-align: center;'>Download the Extracted Page(s).""", unsafe_allow_html=True)
                        st.write("")

                        for i, (file_name, pdf_buffer) in enumerate(st.session_state.extracted_pages):
                            st.download_button(
                                label=f"Download {file_name}",
                                data=pdf_buffer,
                                file_name=file_name,  # Use the provided filename directly
                                mime="application/pdf",
                                key=f"download_extract_{i}"  # Assign a unique key to each download button
                            )

                        # Log the file data only once
                        insert_file_data(
                            name=uploaded_file.name,
                            description="Extracting PDF",
                            status=1,  # Example status
                            content_type=os.path.splitext(uploaded_file.name)[1].lower(),  # Get file extension
                            size=file_size,
                            updated_by=st.session_state.username,  # Get current user's login name
                            updated_on=datetime.datetime.now(),  # Current date and time
                            updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
                        )
                else:
                    st.warning("Please enter page numbers to extract.")
        else:
            st.warning("Please upload a valid PDF File.")

if __name__ == "__page__":
    app()
