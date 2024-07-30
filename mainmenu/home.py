import streamlit as st
import datetime

st.set_page_config(
        page_title="निर्मल : Nirmal",
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

def app():
    # Check if the user is authenticated
    if not st.session_state.authenticated:
        st.error(" 🔒 Please log in before accessing the resource.")
        return
    
    # Title and Description
    st.write(""" <h1 style='text-align: center;'>निर्मल : Powergrid's PDF Converter</h1>""", unsafe_allow_html=True)
    left_co, cent_co,last_co = st.columns(3)
    with left_co:
        st.image("Images/tools-icon.png", width = 420)
    with cent_co:
        st.image("Images/tools-icon.png", width = 420)


    st.markdown('<div style="border-bottom: 2px solid #aaa;"></div>', unsafe_allow_html=True)

    st.markdown("<h2>Who is this application intended for?</h2>", unsafe_allow_html=True)
    st.write("This application is exclusively intended for use by Powergrid Corporation employees. Due to potential security threats posed by existing third-party software solutions, this application has been meticulously developed by the IT department of Powergrid for ensuring data integrity and security.")
    st.warning("It must not be distributed or installed on any computer that is not part of the Powergrid Corporation.")
    st.write('---')

    st.markdown("<h2>How to use this application?</h2>", unsafe_allow_html=True)
    st.write("At the top left corner of the application, there is a toggle arrow. Clicking this arrow opens a sidebar where you can find a list of all the services supported by निर्मल. Each service in the sidebar allows you to perform various format and file conversion tasks when clicked.")
    st.write('---')

    st.write("<h2>The File conversion Formats Supported </h2>", unsafe_allow_html=True)
    st.markdown("<h5>1. Word to PDF</h5>", unsafe_allow_html=True)
    st.write("The application supports seamless conversion from Word (DOCX) documents to PDF format. This conversion ensures that documents maintain their original layout, fonts, and images, while also providing enhanced security and compatibility across different platforms.")
    st.image('./Images/word-to-pdf.png', width=705)

    st.markdown("<h5>2. Merging PDF's</h5>", unsafe_allow_html=True)
    st.write("The application supports merging multiple PDF documents into a single cohesive file. This feature allows users to combine several PDFs into one, simplifying document organization and enhancing workflow efficiency. Merged PDFs retain their individual contents, such as pages, bookmarks, and annotations.")
    st.image('./Images/merge-pdf.png', width=705)

    st.markdown("<h5>3. PNG To PDF</h5>", unsafe_allow_html=True)
    st.write("The application supports converting PNG images to PDF format. This feature allows users to take a Multiple PNG image and convert it into a PDF document, ensuring the image retains its original quality and resolution. This functionality is ideal for making sure that it is easier view on various devices.")
    st.image('./Images/multiplepngtopdf.png', width=705)

    st.markdown("<h5>4. JPG To PDF</h5>", unsafe_allow_html=True)
    st.write("The application provides functionality to convert multiple JPEG (JPG) images into PDF format. This feature enables users to convert individual JPEG images into PDF documents, preserving the image's quality and details. It simplifies the process of sharing images in a universally readable format.")
    st.image('./Images/jpgtopdfbanner.png', width=705)

    st.markdown("<h5>5. XLS To PDF</h5>", unsafe_allow_html=True)
    st.write("The application streamlines the process of converting  Excel (XLS/XLSX) spreadsheets into PDF documents. This feature-rich application ensures that all data, formatting, and calculations from the original spreadsheets are faithfully preserved in the resulting PDF files.")
    st.image('./Images/Exceltopdf.png', width=705)

    st.markdown("<h5>6. Protect PDF</h5>", unsafe_allow_html=True)
    st.write("The application seamlessly secures/protects PDF files with password protection, ensuring sensitive documents remain confidential and accessible only to authorized users while simultaneously ensuring that all textual data and images remains preserved in the original form.")
    st.image('./Images/protectpdfbanner.png', width=705)

    st.markdown("<h5>7. Unlock PDF</h5>", unsafe_allow_html=True)
    st.write("The application effortlessly unlocks password-protected PDF files, converting them back into standard PDFs. This ensures that users can access and manage their documents without restrictions while preserving all textual data and images in their original format.")
    st.image('./Images/unlockpdfbanner.png', width=705)

    st.markdown("<h5>8. PDF to JPG</h5>", unsafe_allow_html=True)
    st.write("The application seamlessly converts PDF files into JPG images, ensuring all textual content and images remain intact. Users can effortlessly convert their PDF documents into image format without compromising on clarity or formatting, making it easy to share, view, and manage.")
    st.image('./Images/multiplejpgtopdf.png', width=705)    
    
    st.markdown("<h5>9. Organise PDF</h5>", unsafe_allow_html=True)
    st.write("The application allows users to add or remove pages from their PDF files with ease. Users can effortlessly manage their PDF documents by inserting or deleting pages as needed, ensuring that their documents are perfectly tailored to their requirements without compromising.")
    st.image('./Images/organise-pdf-banner.png', width=705)    
    
    st.markdown("<h5>10. Split PDF</h5>", unsafe_allow_html=True)
    st.write("The application enables users to split their PDF files into multiple smaller documents. Users can easily divide their PDF files by selecting specific pages or ranges, ensuring that each new document retains the original formatting and content, making it convenient to share and manage.")
    st.image('./Images/split-pdf-banner.png', width=705)    
    
    st.markdown("<h5>11. Extract PDF</h5>", unsafe_allow_html=True)
    st.write("The application allows users to extract specific pages from their PDF files. Users can select the pages they want to extract and save them as a new PDF document, ensuring that the formatting and content remain intact. This feature makes it easy to focus on and share particular sections of a larger document.")
    st.image('./Images/extract-pdf-banner.png', width=705)
    
    st.markdown("<h5>12. Compress PDF</h5>", unsafe_allow_html=True)
    st.write("The application enables users to compress PDF files, reducing their size without compromising the quality of the content. This feature helps in managing storage space and facilitates easier sharing and faster uploading of documents, ensuring that all textual content and images remain clear and intact.")
    st.image('./Images/compress-pdf-banner.png', width=705)

    st.markdown("<h5>13. Watermark PDF</h5>", unsafe_allow_html=True)
    st.write("The application enables users to add watermark to the  PDF files without compromising the quality of the content. It provides users with the option to choose between various fonts , fonts colours and fonts size, simultaneousy ensuring that all textual content and images remain clear and intact.")
    st.image('./Images/watermark-pdf-banner.png', width=705)
    
    st.markdown("<h5>14. Digital Sign PDF</h5>", unsafe_allow_html=True)
    st.write("The application allows users to digitally sign PDF files, maintaining the integrity and quality of the content ensuring that the digital signature is applied securely and accurately, incorporating details such as the organization name, time, and date at the bottom-left of the page.")
    st.image('./Images/sign-pdf-banner.png', width=705)

    st.write("---")

    st.markdown("<h2>How is निर्मल secure?</h2>", unsafe_allow_html=True)
    st.write(" When a user uploads a file, निर्मल reads the initial bytes of the file. It compares these bytes with predefined magic numbers associated with supported file formats (e.g., PDF, DOCX, PNG, JPEG). By matching the magic numbers, निर्मल ensures that the uploaded file is indeed in the expected format. Hence redcuing the effectiveness of potential attacks and threats.")

    st.write('---')
    footer = """
    <style>
    .main-footer {
        font-size: 12px;
        color: gray;
        text-align: center; 
        bottom: 0;
        width: 100%;
    }
    </style>
    <div class="main-footer">
        <h6 style='text-align: center;'>Powergrid Corporation of India &copy; """ + str(get_current_year()) + """ All rights reserved.</h6>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

if __name__ == "__page__":
    app()
