from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from gtts import gTTS
import PyPDF2
import os

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
app.secret_key = b"NL[\xdb,\xb1\x80z\x94\xda\xe2\x99'~7\xda\xf8\x83\xc7\t\x15\x15\xf1<"


# Configure allowed file extensions
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}


# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Function to convert text to speech and save as an MP3 file
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)


# Database connection
client = MongoClient("mongodb://localhost:27017/")
db = client['your_database']
collection = db['uploads']


# Route to render the home page
@app.route('/')
def home():
    return render_template('index.html')


# Route to handle file upload and conversion
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            flash('No file part, please select a PDF file.', 'error')
            return redirect(request.url)

        file = request.files['pdf']
        if file.filename == '':
            flash('No selected file. Please choose a PDF file.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_data = file.read()
                collection.insert_one({"filename": filename, "file_data": file_data})
                print("File has been saved to the database")

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                save_filename = os.path.splitext(filename)[0]
                speech_file = f'{save_filename}.mp3'
                speech_file_path = os.path.join('static', 'mp3files', speech_file)
                text = extract_text_from_pdf(file_path)
                text_to_speech(text, speech_file_path)
                os.remove(file_path)
                print("Text extracted and converted to speech")

                flash(f'File "{filename}" successfully uploaded and converted to "{speech_file}".', 'success')
                return render_template('upload.html', speech_file=speech_file)

            except Exception as e:
                flash(f'Error processing file: {e}', 'error')
                return redirect(request.url)

        else:
            flash('Please select an acceptable file type (.pdf).', 'error')
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return redirect("/")

    return render_template('contact.html')


@app.route('/terms')
def terms():
    return render_template('TOS.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/help')
def helps():
    return render_template('help.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
