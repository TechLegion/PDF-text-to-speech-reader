from flask import Flask, render_template, request, redirect, flash, url_for
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from gtts import gTTS
import PyPDF2


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
    except Exception as e:
        print("Error:", e)
    return text


# Initialize Flask application
app = Flask(__name__)
# Set secret key for session management and form handling
app.secret_key = b"NL[\xdb,\xb1\x80z\x94\xda\xe2\x99'~7\xda\xf8\x83\xc7\t\x15\x15\xf1<"

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


# Function to convert text to speech and save as an MP3 file
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)


client = MongoClient("mongodb://localhost:27017/")


# Route to render the home page
@app.route('/')
def home():
    return render_template('index.html')


# Route to handle file upload and conversion
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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

                # Extract text from the PDF and convert it to speech
                text = extract_text_from_pdf(file_path)
                text_to_speech(text, speech_file_path)
                print("This is the speech file path " + speech_file_path)
                print(f"This is what you have in url_for on upload.html 'static/mp3files/{speech_file_path.split('/')[-1]}")
                print("Text extracted and converted to speech")

                # Flash success message and render the upload template with the path to the speech file
                flash(f'File "{filename}" successfully uploaded and converted to "{speech_file}".', 'success')

                return render_template('upload.html', speech_file=speech_file)

            except Exception as e:
                # Flash error message in case of any exception
                flash(f'Error processing file: {e}', 'error')
                return redirect(request.url)

        else:
            # Flash error message if the file type is not allowed
            flash('Please select an acceptable file type (.pdf).', 'error')
            return redirect(request.url)

    return render_template('upload.html')


# Route to render the about page
@app.route('/about')
def about():
    return render_template('about.html')


# Route to handle contact form and render the contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission (e.g., save data to database or send email)
        return redirect("/")

    return render_template('contact.html')


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
