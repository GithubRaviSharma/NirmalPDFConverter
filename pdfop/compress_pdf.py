import streamlit as st
import subprocess
import os
import shutil
import datetime
import socket
import pyodbc

st.set_page_config(
    page_title="निर्मल: PDF Compressor",
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

# Function to compress PDF via Ghostscript command line interface
def compress(input_file_path, output_file_path, power=0):
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }

    # Get Ghostscript executable path
    gs = get_ghostscript_path()

    st.info("Compressing PDF ...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call([
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS={}".format(quality[power]),
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-sOutputFile={}".format(output_file_path),
        input_file_path,
    ])
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    st.success(f"The PDF was compressed to {initial_size / 1024:.2f} KB with Compression ratio: {ratio:.2%}.")

    return output_file_path

# Function to find Ghostscript executable
def get_ghostscript_path():
    # Specify the full path to GhostScript executable here
    gs_path = r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe" # Adjust path as per your installation
    if os.path.exists(gs_path):
        return gs_path
    else:
        raise FileNotFoundError(f"No GhostScript executable found at {gs_path}. Please check your installation.")

# Main Streamlit app
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
    
    st.markdown("<h1 style='text-align: center;'><  निर्मल: PDF Size Compressor  ></h1>", unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 3])

    # Adding elements to the second column
    with col1:
        st.image('./Images/compress-pdf.png', width=700)

    uploaded_file = st.file_uploader("*Upload the PDF that you want to compress.", type="pdf", key="compress_uploader")

    if uploaded_file:
        if is_pdf(uploaded_file):
            st.success("PDF File uploaded successfully!")
            file_size = len(uploaded_file.getvalue())
            power = st.selectbox("*Choose the Compression Level.", ["Default", "Prepress", "Printer", "Ebook", "Screen"], index=2)

            if st.button("Compress PDF"):
                if power == "Default":
                    power = 0
                elif power == "Prepress":
                    power = 1
                elif power == "Printer":
                    power = 2
                elif power == "Ebook":
                    power = 3
                elif power == "Screen":
                    power = 4

                # Create temporary paths
                temp_folder = "temp"
                os.makedirs(temp_folder, exist_ok=True)
                input_file_path = os.path.join(temp_folder, uploaded_file.name)
                output_file_path = os.path.join(temp_folder, "compressed.pdf")

                # Save uploaded file to temp folder
                with open(input_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Compress PDF
                compressed_file_path = compress(input_file_path, output_file_path, power)

                # Offer download link for compressed PDF
                if compressed_file_path:
                    st.download_button(
                        label="Download Compressed PDF",
                        data=open(compressed_file_path, 'rb').read(),
                        file_name="compressed.pdf",
                        mime="application/pdf"
                    )

                    # Log file data to the database
                    insert_file_data(
                        name=uploaded_file.name,
                        description="Compress PDF",
                        status=1,
                        content_type=os.path.splitext(uploaded_file.name)[1].lower(),
                        size=file_size,
                        updated_by=st.session_state.username,
                        updated_on=datetime.datetime.now(),
                        updated_from=socket.gethostbyname(socket.gethostname())
                    )

                # Clean up temp folder
                shutil.rmtree(temp_folder)
            
        else:
            st.warning("Please upload a valid PDF File.")

if __name__ == "__page__":
    app()
