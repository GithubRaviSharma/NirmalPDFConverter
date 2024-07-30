import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tempfile
import pyodbc
import datetime
import socket
import os
import pymupdf

st.set_page_config(
    page_title="निर्मल: Watermark PDF",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Function to check if the file is a PDF using magic number
def is_pdf(file):
    file.seek(0)
    magic_number = file.read(4)
    file.seek(0)  # Reset file pointer to the beginning
    return magic_number == b'%PDF'

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

            # Display success message
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

# Define a set of professional fonts to use
PROFESSIONAL_FONTS = {
    "Arial": "arial.ttf",
    "Times New Roman": "timesnewroman.ttf",
    "Verdana": "verdana.ttf",
    "Courier New": "cour.ttf",
    "Comic Sans MS": "comic.ttf",
    "Trebuchet MS": "trebuc.ttf",
    "Impact": "impact.ttf",
    "Tahoma": "tahoma.ttf",
    "Palatino Linotype": "pala.ttf",
    "Calibri": "calibri.ttf"
}


def create_watermark_image(text, width, height, font_path, font_size, font_color):
    # Create an image with transparent background
    watermark_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_image)

    # Load the selected font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size and position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # Draw the text onto the image
    draw.text((x, y), text, font=font, fill=font_color)

    # Rotate the image
    watermark_image = watermark_image.rotate(45, expand=1)

    # Save the image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        watermark_image.save(tmp_file, format="PNG")
        tmp_file.seek(0)
        return tmp_file.name

def add_watermark(pdf_file, watermark_text, font_path, font_size, font_color):
    # Open the uploaded PDF file
    pdf_document = pymupdf.open(stream=pdf_file.read(), filetype="pdf")

    # Create the watermark image from text
    first_page = pdf_document.load_page(0)
    watermark_image_path = create_watermark_image(watermark_text, int(first_page.rect.width), int(first_page.rect.height), font_path, font_size, font_color)

    # Apply the watermark to each page of the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        page.insert_image(page.rect, filename=watermark_image_path)

    # Save the watermarked PDF to a BytesIO object
    output_pdf = BytesIO()
    pdf_document.save(output_pdf)
    output_pdf.seek(0)

    return output_pdf

def main():
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

    if not st.session_state.get('authenticated', False):
        st.error(" 🔒 Please log in before accessing the resource.")
        return

    st.markdown("<h1 style='text-align: center;'>< निर्मल: Watermark PDF Adder ></h1>", unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the first column
    with col1:
        st.image('./Images/add-watermark-pdf.webp', width=720)

    # File uploader
    uploaded_file = st.file_uploader("*Choose a PDF file that you want to add watermark to.", type="pdf", key="watermark_uploader")
    
    if uploaded_file:
        if is_pdf(uploaded_file):
            st.success("PDF File uploaded successfully!")
            st.write("")

            # Watermark options
            watermark_text = st.text_input("*Add the Watermark Text", "Sample Watermark")
            st.write("")
            font_size = st.slider("*Choose the Font Size", min_value=10, max_value=100, value=50)
            st.write("")           
            font_color = st.color_picker("*Choose the Font Color", "#808080")  # Default to gray
            st.write("")
            
            # Choose from predefined professional fonts
            font_options = list(PROFESSIONAL_FONTS.keys())
            selected_font_name = st.selectbox("*Select the Font", font_options)
            font_path = PROFESSIONAL_FONTS[selected_font_name]

            # Button to add watermark
            if st.button("Add Watermark"):
                try:
                    # Add watermark to the uploaded PDF file
                    watermarked_pdf = add_watermark(uploaded_file, watermark_text, font_path, font_size, font_color)
                    st.success("Watermark added to PDF!")

                    # Provide a download link for the watermarked PDF file
                    st.download_button(
                        label="Download Watermarked PDF",
                        data=watermarked_pdf,
                        file_name="watermarked.pdf",
                        mime="application/pdf"
                    )

                    # Insert file data into database
                    insert_file_data(
                        name=uploaded_file.name,
                        description="Watermark PDF",
                        status=1,
                        content_type=os.path.splitext(uploaded_file.name)[1].lower(),
                        size=len(uploaded_file.getvalue()),
                        updated_by=st.session_state.get('username', 'unknown'),
                        updated_on=datetime.datetime.now(),
                        updated_from=socket.gethostbyname(socket.gethostname())
                    )
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload a valid PDF File!")
   
if __name__ == "__page__":
    main()