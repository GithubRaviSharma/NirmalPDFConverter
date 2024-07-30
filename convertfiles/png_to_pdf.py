import streamlit as st
from PIL import Image
import tempfile
import os
from fpdf import FPDF
import datetime
import socket
import pyodbc

# Set Streamlit page configuration
st.set_page_config(
    page_title="निर्मल: PNG to PDF",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.logo("Images/powergrid.webp")


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
            # Display success message
            # st.success(f"File log updated successfully!.")

    except pyodbc.Error as e:
        st.error(f"Error inserting file data: {e}")
        st.write("SQL Error:", e)
        st.write("SQL State:", e.args[0])
        st.write("SQL Message:", e.args[1])
    except Exception as ex:
        st.error(f"Unexpected error: {ex}")
    finally:
        if conn:
            conn.close()

# Function to check if a file is a PNG
def is_png(file):
    # PNG magic number (header)
    png_magic_number = b'\x89PNG\r\n\x1a\n'

    # Read the first 8 bytes of the file
    first_bytes = file.read(8)

    # Check if the file header matches the PNG magic number
    return first_bytes[:8] == png_magic_number

# Main Streamlit application function
def app():
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

    # Streamlit setup
    st.markdown("<h1 style='text-align: center;'><  निर्मल: PNG To PDF Converter  ></h1>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 3])

    with col2:
        st.image('./Images/png-pdf-banner.png', width=470)

    # File uploader for PNG files
    uploaded_files = st.file_uploader("*Upload multiple PNG files to convert to PDF.", type="png", accept_multiple_files=True, key="multipng_uploader")


    if uploaded_files:
        temp_png_paths = []
    
        for uploaded_file in uploaded_files:
            if is_png(uploaded_file): 
                file_size = len(uploaded_file.getvalue())
                
                # Insert file data into database
                insert_file_data(
                    name=uploaded_file.name,
                    description="PNG to PDF",
                    status=1,  # Example status
                    content_type=os.path.splitext(uploaded_file.name)[1].lower(),  # Get file extension
                    size=file_size,
                    updated_by=st.session_state.username,  # Get current user's login name
                    updated_on=datetime.datetime.now(),  # Current date and time
                    updated_from=socket.gethostbyname(socket.gethostname())  # Example of retrieving hostname
                )
                
                # Save each uploaded file to a temporary PNG file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_png:
                    temp_png.write(uploaded_file.getbuffer())
                    temp_png_paths.append(temp_png.name)
            else:
                st.warning("Please upload a valid PNG File.")
                return
        
        st.success("Image file(s) uploaded successfully!")
        st.image(uploaded_files,  use_column_width=True)
        st.markdown("<h6 style='text-align: center;'><  Uploaded PNG File(s)  ></h6>", unsafe_allow_html=True)
        st.success("Converting the File(s) to PDF ...")



    
        if temp_png_paths:
            try:
                # Convert PNG files to PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf_path = temp_pdf.name

                    # Create a PDF document
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)

                    for temp_png_path in temp_png_paths:
                        # Open the PNG image using PIL
                        image = Image.open(temp_png_path)

                        # Add a page to the PDF
                        pdf.add_page()

                        # Calculate image dimensions to fit within the PDF page
                        img_width_mm, img_height_mm = pdf.w - 2 * pdf.l_margin, pdf.h - 2 * pdf.b_margin
                        img_width, img_height = image.size
                        aspect_ratio = img_width / img_height

                        # Determine orientation based on aspect ratio
                        if aspect_ratio >= 1:
                            pdf.image(temp_png_path, x=pdf.l_margin, y=pdf.t_margin, w=img_width_mm)
                        else:
                            pdf.image(temp_png_path, x=pdf.l_margin, y=pdf.t_margin, h=img_height_mm)

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
                st.error(f"Error converting PNG to PDF: {ex}")
            finally:
                # Clean up temporary files
                for temp_png_path in temp_png_paths:
                    os.remove(temp_png_path)
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

# Main application entry point
if __name__ == "__page__":
    app()


