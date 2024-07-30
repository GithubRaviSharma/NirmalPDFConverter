import streamlit as st
from PIL import Image
from fpdf import FPDF
import tempfile
import os
import datetime
import socket
import pyodbc

# Function to get the current year
def get_current_year():
    return datetime.datetime.now().year

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

# Function to insert file data into the database
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

# Function to check if a file is a JPEG
def is_jpeg(file):
    # JPEG magic numbers (headers)
    jpeg_magic_numbers = [
        b'\xFF\xD8\xFF\xE0',
        b'\xFF\xD8\xFF\xE1',
        b'\xFF\xD8\xFF\xE2',
        b'\xFF\xD8\xFF\xE8'
    ]

    # Read the first 4 bytes of the file
    first_bytes = file.read(4)

    # Check if the file header matches any of the JPEG magic numbers
    for magic_number in jpeg_magic_numbers:
        if first_bytes.startswith(magic_number):
            return True

    return False

# Main application function encapsulating Streamlit logic
def app():
    # Set Streamlit page configuration
    st.set_page_config(
    page_title="निर्मल: JPG to PDF",
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
    
    # Title and description
    st.markdown("<h1 style='text-align: center;'><  निर्मल: JPG To PDF Converter  ></h1>", unsafe_allow_html=True)
    st.write("")

    # Layout setup
    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the second column
    with col2:
        st.image('./Images/jpg-pdf-banner.png', width=470)
    
    # File uploader to upload a single JPEG file
    uploaded_file = st.file_uploader("*Upload a JPG/JPEG file that you want to convert.", type=["jpg", "jpeg"], accept_multiple_files=False, key="singlejpg_uploader")

    if uploaded_file:
        if is_jpeg(uploaded_file):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_jpg:
                temp_jpg.write(uploaded_file.getbuffer())
                temp_jpg_path = temp_jpg.name

                # Insert file data into the database
                file_size = len(uploaded_file.getvalue())
                insert_file_data(
                    name=uploaded_file.name,
                    description="JPG to PDF",
                    status=1,  # Example status
                    content_type=os.path.splitext(uploaded_file.name)[1].lower(),  # Get file extension
                    size=file_size,
                    updated_by=st.session_state.username,  # Get current user's login name
                    updated_on=datetime.datetime.now(),  # Current date and time
                    updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
                )

            st.success("Image file uploaded successfully!")
            st.image(uploaded_file,  use_column_width=True)
            st.markdown("<h6 style='text-align: center;'><  Uploaded JPG File  ></h6>", unsafe_allow_html=True)
            st.success("The JPG file was successfully converted to PDF!")


            # Convert the JPEG file to PDF
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf_path = temp_pdf.name

                    # Create a PDF document
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)

                    # Open the JPEG image using PIL
                    image = Image.open(temp_jpg_path)

                    # Add a page to the PDF
                    pdf.add_page()

                    # Calculate image dimensions to fit within the PDF page
                    img_width_mm, img_height_mm = pdf.w - 2 * pdf.l_margin, pdf.h - 2 * pdf.b_margin
                    img_width, img_height = image.size
                    aspect_ratio = img_width / img_height

                    # Determine orientation based on aspect ratio
                    if aspect_ratio >= 1:
                        pdf.image(temp_jpg_path, x=pdf.l_margin, y=pdf.t_margin, w=img_width_mm)
                    else:
                        pdf.image(temp_jpg_path, x=pdf.l_margin, y=pdf.t_margin, h=img_height_mm)

                    # Close the image
                    image.close()

                    # Save the PDF document
                    pdf.output(temp_pdf_path)

                # Provide a download button for the converted PDF
                with open(temp_pdf_path, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name="converted.pdf",
                        mime="application/pdf"
                    )

            except Exception as ex:
                st.error(f"Error converting JPG to PDF: {ex}")
            finally:
                # Clean up temporary files
                os.remove(temp_jpg_path)
                os.remove(temp_pdf_path)

        else:
            st.warning("Please upload a valid JPG/JPEG file.")

# Main application logic
if __name__ == "__page__":
    app()
