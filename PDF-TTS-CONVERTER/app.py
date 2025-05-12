from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.utils import secure_filename
import os
from pymongo import *
from bson.objectid import ObjectId
from gtts import gTTS
import PyPDF2
from dotenv import load_dotenv
# OCR imports
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Function to extract text from a PDF file, with OCR fallback
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page_text = reader.pages[page_num].extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print("Error (PyPDF2):", e)
    # Debug print
    print(f"Extracted text (PyPDF2): {repr(text[:500])}")
    # If no text found, try OCR
    if not text.strip():
        print("No text found with PyPDF2, attempting OCR fallback...")
        try:
            images = convert_from_path(pdf_path)
            ocr_text = ""
            for i, image in enumerate(images):
                ocr_page = pytesseract.image_to_string(image)
                ocr_text += ocr_page
            text = ocr_text
            print(f"Extracted text (OCR): {repr(text[:500])}")
        except Exception as e:
            print("Error (OCR fallback):", e)
    return text


# Initialize Flask application
app = Flask(__name__)
# Set secret key for session management and form handling
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

client = MongoClient('localhost', 27017)
db = client.pdf_reader_database
files_uploaded = db.files
# Configure upload folder and allowed file extensions
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Create directories if they don't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists('static/mp3files'):
    os.makedirs('static/mp3files')


# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Function to limit the text length to approximately fit a 5-minute audio duration
def limit_text_length(text, max_duration_minutes=5):
    words_per_minute = 150  # Average speaking rate
    max_words = words_per_minute * max_duration_minutes
    return ' '.join(text.split()[:max_words])


# Route to render the home page
@app.route('/')
def home():
    return render_template('index.html')


# Route to handle file upload and conversion
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        voice = request.form['voice']
        # Check if the post request has the file part
        if 'pdf' not in request.files:
            flash('No file part, please select a PDF file.', 'error')
            return redirect(request.url)

        file = request.files['pdf']
        # Check if the user has actually selected a file
        if file.filename == '':
            flash('No selected file. Please choose a PDF file.', 'error')
            return redirect(request.url)

        # Check if the selected file is allowed and process it
        if file and allowed_file(file.filename):
            try:
                # Secure the filename and save the file to the upload folder
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                print("File has been saved to the upload folder")

                # Generate the output MP3 file path
                save_filename = os.path.splitext(filename)[0]
                speech_file = f'{save_filename}.mp3'
                speech_file_path = os.path.join('static', 'mp3files', speech_file)
                print(f"Mp3 file {speech_file} saved in static/mp3files folder")

                # Extract text from the PDF (with debug print and OCR fallback)
                text = extract_text_from_pdf(file_path)
                # Limit the text length to fit the desired audio duration
                limited_text = limit_text_length(text)

                # Prevent empty audio
                if not limited_text.strip():
                    flash('No text could be extracted from the PDF. Please try another file.', 'error')
                    return redirect(request.url)

                # Convert limited text to speech
                tts = gTTS(text=limited_text, lang=voice)
                tts.save(speech_file_path)

                print("This is the speech file path " + speech_file_path)
                print(f"This is what you have in url_for on upload.html 'static/mp3files/{speech_file_path.split('/')[-1]}")
                print("Text extracted and converted to speech")

                # Flash success message and render the upload template with the path to the speech file
                flash(f'"{filename}" successfully uploaded', 'success')
                files_uploaded.insert_one({'file_name': save_filename})
                return render_template('upload.html', speech_file=speech_file)

            except Exception as e:
                # Flash error message in case of any exception
                flash(f'Error processing file: {e}', 'error')
                return redirect(request.url)

        else:
            # Flash error message if the file type is not allowed
            flash('Please select the acceptable file type (.pdf). You selected a wrong file format', 'error')
            return redirect(request.url)

    return render_template('upload.html')


# Route to render the about page
@app.route('/about')
def about():
    return render_template('about.html')


# Route to handle contact form and render the contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Store data in session to retain input if an error occurs
        session["name"] = name
        session["email"] = email
        session["message"] = message

        if not name or not email or not message:
            flash("All fields are required!", "error")
            return redirect("/contact")  # Redirect to retain form data

        # Process the form (e.g., save to database, send email, etc.)
        flash("Message sent successfully!", "success")

        # Clear session after successful submission
        session.pop("name", None)
        session.pop("email", None)
        session.pop("message", None)

        return redirect("/contact")

    return render_template("contact.html",
                           name=session.get("name", ""),
                           email=session.get("email", ""),
                           message=session.get("message", ""))


# Route to render the terms of service page
@app.route('/terms')
def terms():
    return render_template('TOS.html')


# Route to render the privacy policy page
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


# Route to render the help page
@app.route('/help')
def helps():
    return render_template('help.html')


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
