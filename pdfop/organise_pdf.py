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
    except pyodbc.Error as e:
        st.error(f"Error inserting file data: {e}")
    except Exception as ex:
        st.error(f"Unexpected error: {ex}")
    finally:
        if conn:
            conn.close()

# Function to add pages to a PDF
def add_pdf_pages(input_pdf, pages_to_add):
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    for page_data in pages_to_add:
        pdf_writer.add_page(page_data)

    # Save to a bytes buffer
    pdf_buffer = io.BytesIO()
    pdf_writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer

# Function to delete pages from a PDF
def delete_pdf_pages(input_pdf, pages_to_delete):
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        if page_num + 1 not in pages_to_delete:
            pdf_writer.add_page(pdf_reader.pages[page_num])

    # Save to a bytes buffer
    pdf_buffer = io.BytesIO()
    pdf_writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer

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
        page_title="निर्मल: PDF Organiser",
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
        st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {datetime.datetime.now().year} All rights reserved.</h6>""", unsafe_allow_html=True)

    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return
    
    st.markdown("<h1 style='text-align: center;'><  निर्मल: PDF Organiser ></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 3])
    
    # Adding elements to the second column
    with col2:
        st.image('./Images/how-to-create-pdf.png', width=460)   
    # Selectbox for PDF operations
    selected_option = st.selectbox("*Select PDF Operation.", [ 'Add Pages', 'Delete Pages'])
    if selected_option == 'Add Pages':
        uploaded_main_file = st.file_uploader("*Upload the PDF file you want to add pages to.", type="pdf", key="add_main_uploader")

        if uploaded_main_file:
            if is_pdf(uploaded_main_file):
                st.success("Your PDF File uploaded successfully!")
                file_size = len(uploaded_main_file.getvalue())
                pdf_reader = PdfReader(uploaded_main_file)
                total_pages = len(pdf_reader.pages)
                st.write("")
                st.markdown(f"<h6 style='text-align: center;'>The {uploaded_main_file.name} has {total_pages} pages.</h6>", unsafe_allow_html=True)
                st.write("")

                uploaded_additional_file = st.file_uploader("*Upload PDF file to add pages from.", type="pdf", key="add_additional_uploader")

                if uploaded_additional_file:
                    if is_pdf(uploaded_additional_file):
                        st.success("Additional PDF File uploaded successfully!")
                        file_size = len(uploaded_additional_file.getvalue())
                        pdf_reader = PdfReader(uploaded_additional_file)
                        total_pages = len(pdf_reader.pages)
                        st.write("")
                        st.markdown(f"<h6 style='text-align: center;'>The {uploaded_additional_file.name} has {total_pages} pages.</h6>", unsafe_allow_html=True)
                        st.write("")

                        # Get the specific pages to add
                        pages_to_add = st.text_input("Enter page numbers to add from additional PDF (comma-separated).", key="add_page_numbers")

                        if st.button("Add Pages"):
                            if pages_to_add:
                                # Convert pages_to_add to a list of integers
                                try:
                                    pages_to_add = [int(num.strip()) for num in pages_to_add.split(',')]
                                except ValueError:
                                    st.warning("Please enter valid page numbers.")
                                    return

                                if pages_to_add:
                                    additional_pdf_pages = []
                                    for page_num in pages_to_add:
                                        if 1 <= page_num <= len(pdf_reader.pages):
                                            additional_pdf_pages.append(pdf_reader.pages[page_num - 1])

                                    merged_pdf = add_pdf_pages(uploaded_main_file, additional_pdf_pages)

                                    st.success("Page(s) successfully added to the PDF!")
                                    st.download_button(
                                        label=f"Download Merged PDF",
                                        data=merged_pdf,
                                        file_name=f"Merged_{uploaded_main_file.name}",
                                        mime="application/pdf",
                                        key="download_merged"
                                    )
                                    # Log the file data
                                    insert_file_data(
                                        name=uploaded_main_file.name,
                                        description="Organising PDF",
                                        status=1,
                                        content_type=os.path.splitext(uploaded_main_file.name)[1].lower(),
                                        size=file_size,
                                        updated_by=st.session_state.username,
                                        updated_on=datetime.datetime.now(),
                                        updated_from=socket.gethostbyname(socket.gethostname())
                                    )
                            else:
                                st.warning("Please enter the page numbers to add.")

                    else:
                        st.warning("Please upload a valid additional PDF file.")

            else:
                st.warning("Please upload a valid main PDF file.")

    elif selected_option == 'Delete Pages':
        uploaded_file = st.file_uploader("*Upload a PDF file from which you want to delete pages.", type="pdf", key="delete_uploader")

        if uploaded_file:
            if is_pdf(uploaded_file):
                st.success("PDF File uploaded successfully!")
                file_size = len(uploaded_file.getvalue())
                pdf_reader = PdfReader(uploaded_file)
                total_pages = len(pdf_reader.pages)
                st.write("")
                st.markdown(f"<h6 style='text-align: center;'>The {uploaded_file.name} has {total_pages} pages.</h6>", unsafe_allow_html=True)
                st.write("")

                # Get the specific pages to delete
                pages_to_delete = st.text_input("*Enter page numbers to delete (comma-separated).", key="delete_page_numbers")

                if st.button("Delete Pages"):
                    if pages_to_delete:
                        # Convert pages_to_delete to a list of integers
                        try:
                            pages_to_delete = [int(num.strip()) for num in pages_to_delete.split(',')]
                        except ValueError:
                            st.warning("Please enter valid page numbers.")
                            return

                        if pages_to_delete:
                            deleted_pdf = delete_pdf_pages(uploaded_file, pages_to_delete)

                            st.success("Page(s) successfully deleted from the PDF!")
                            st.download_button(
                                label=f"Download Updated PDF",
                                data=deleted_pdf,
                                file_name=f"Updated_{uploaded_file.name}",
                                mime="application/pdf",
                                key="download_deleted"
                            )

                            # Log the file data
                            insert_file_data(
                                name=uploaded_file.name,
                                description="Organising PDF",
                                status=1,
                                content_type=os.path.splitext(uploaded_file.name)[1].lower(),
                                size=file_size,
                                updated_by=st.session_state.username,
                                updated_on=datetime.datetime.now(),
                                updated_from=socket.gethostbyname(socket.gethostname())
                            )
                    else:
                        st.warning("Please enter the page numbers to delete.")

            else:
                st.warning("Please upload a valid PDF file.")

    st.write("")
    st.write("")

# Main entry point of the app
if __name__ == "__page__":
    app()
