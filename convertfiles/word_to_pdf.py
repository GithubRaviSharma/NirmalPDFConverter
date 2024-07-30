import streamlit as st
from docx2pdf import convert
import tempfile
import os
import pythoncom
import datetime
import pyodbc
import socket

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


# Main Streamlit application function
def app():
    st.set_page_config(
        page_title="निर्मल: DOCX to PDF",
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

    pythoncom.CoInitialize()

    st.markdown("<h1 style='text-align: center;'><  निर्मल: DOC To PDF Converter  ></h1>", unsafe_allow_html=True)
    st.image('./Images/word-to-pdf-color.webp', width=600)

    uploaded_file = st.file_uploader("*Upload a Word file that you want to convert.", type="docx", key="docx_uploader")

    if uploaded_file is not None:
        file_size = len(uploaded_file.getvalue())
        docx_magic_number = b"\x50\x4B\x03\x04"  # Magic number for DOCX files
        first_bytes = uploaded_file.read(len(docx_magic_number))
        uploaded_file.seek(0)

        if first_bytes == docx_magic_number:
            st.success("Word Document uploaded successfully!")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                temp_docx.write(uploaded_file.read())
                temp_docx_path = temp_docx.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf_path = temp_pdf.name

            convert(temp_docx_path, temp_pdf_path)

            with open(temp_pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name="converted.pdf",
                    mime="application/pdf"
                )

            os.remove(temp_docx_path)
            os.remove(temp_pdf_path)
        else:
            st.warning("Please upload a valid DOCX file.")

        
        insert_file_data(
                name=uploaded_file.name,
                description = "Word to PDF",
                status=1,  # Example status
                content_type=os.path.splitext(uploaded_file.name)[1].lower(),  # Get file extension
                size=file_size,
                updated_by= st.session_state.username ,  # Get current user's login name
                updated_on=datetime.datetime.now(),  # Current date and time
                updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
            )


    pythoncom.CoUninitialize()

if __name__ == "__page__":
    app()
