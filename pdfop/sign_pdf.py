import streamlit as st
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from io import BytesIO
import tempfile
import pymupdf
import pyodbc
import io
import datetime
import socket
import os

st.set_page_config(
    page_title="निर्मल: Sign PDF",
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


def sign_pdf(p12_file, password, pdf, add_footer=False):
    try:
        # Create a temporary file for the PKCS#12 data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.p12') as temp_p12_file:
            temp_p12_file.write(p12_file.read())
            temp_p12_path = temp_p12_file.name
        
        # Load the PKCS#12 file with the signer information
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=temp_p12_path, passphrase=password.encode('utf-8')
        )
        
        # Read the PDF data
        pdf_data = pdf.read()
        
        # Log the size of the original PDF
        # original_pdf_size = len(pdf_data)
        # st.write(f"Original PDF size: {original_pdf_size} bytes")
        
        # Open the PDF document
        pdf_stream = BytesIO(pdf_data)
        w = IncrementalPdfFileWriter(pdf_stream)
        
        # Sign the PDF
        signed_pdf_stream = BytesIO()
        signers.sign_pdf(
            w, signers.PdfSignatureMetadata(field_name='Signature1'),
            signer=signer,
        )
        
        # Save the signed PDF
        w.write(signed_pdf_stream)
        signed_pdf_stream.seek(0)
        
        # Log the size of the signed PDF
        # signed_pdf_size = len(signed_pdf_stream.getvalue())
        # st.write(f"Signed PDF size: {signed_pdf_size} bytes")
        
        if add_footer:
            # Add footer to signed PDF
            signed_pdf_bytes = signed_pdf_stream.getvalue()
            signed_pdf_stream = BytesIO(signed_pdf_bytes)
            
            # Open signed PDF with PyMuPDF
            pdf_document = pymupdf.open(stream=signed_pdf_stream, filetype="pdf")
            footer_text = f"Signed by: Powergrid\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Add footer to each page
            for page_number in range(len(pdf_document)):
                page = pdf_document.load_page(page_number)
                page.insert_text(
                    (26, page.rect.height - 30),  # Position (left, bottom)
                    footer_text,
                    fontsize=10,
                    color=(0, 0, 0)
                )
            
            # Save PDF with footer
            final_pdf_stream = BytesIO()
            pdf_document.save(final_pdf_stream, garbage=4, deflate=True)
            final_pdf_stream.seek(0)
            
            return final_pdf_stream.getvalue()
        
        return signed_pdf_stream.getvalue()
    
    except Exception as e:
        raise RuntimeError(f"Error during PDF signing: {e}")

# Streamlit UI
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
        st.markdown(f"""<h6 style='text-align: center;'>Powergrid &copy; {datetime.datetime.now().year} All rights reserved.</h6>""", unsafe_allow_html=True)

    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return
    
    st.markdown("<h1 style='text-align: center;'><  निर्मल: Digital PDF Signature  ></h1>", unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the second column
    with col2:
        st.image('./Images/sign_pdf.webp', width=430)    
    
    # Upload PDF file
    uploaded_file = st.file_uploader("*Choose a PDF file that you want to sign.", type="pdf", key="sign_uploader")

    if uploaded_file:
        if is_pdf(uploaded_file):
            # Upload PKCS#12 file
            uploaded_p12 = st.file_uploader("*Choose a Digital Certificate to sign from.", type="p12", key="certificate_uploader")
            # Password for PKCS#12 file
            password = st.text_input("*Please input password for the digital certificate.", type="password", key="password_input")
            # Checkbox to add footer
            add_footer = st.checkbox("Add footer to the PDF", value=False)
        
            # Button to sign the PDF
            if st.button("Sign PDF"):
                if uploaded_file and uploaded_p12 and password:
                        try:
                            # Convert uploaded files to BytesIO
                            pdf_bytes = BytesIO(uploaded_file.read())
                            p12_bytes = BytesIO(uploaded_p12.read())
                         
                            # Sign the PDF and add footer if selected
                            signed_pdf_bytes = sign_pdf(p12_bytes, password, pdf_bytes, add_footer=add_footer)
                         
                            # Provide a download link for the signed PDF
                            st.success("PDF signed successfully!")
                            st.download_button(
                                label="Download Signed PDF",
                                data=signed_pdf_bytes,
                                file_name="signed_pdf.pdf",
                                mime="application/pdf",
                            )
                            insert_file_data(
                                name=uploaded_file.name,
                                description="Signing PDF",
                                status=1,
                                content_type=os.path.splitext(uploaded_file.name)[1].lower(),
                                size=len(uploaded_file.getvalue()),
                                updated_by=st.session_state.get('username', 'unknown'),
                                updated_on=datetime.datetime.now(),
                                updated_from=socket.gethostbyname(socket.gethostname())
                                )
                        except Exception as e:
                            st.error(f"Please enter a valid Password.")
                else:
                    st.error("Please upload both Digital Certificate and the password.")
        else:
            st.warning("Please upload a valid PDF File.")

if __name__ == "__page__":
    app()