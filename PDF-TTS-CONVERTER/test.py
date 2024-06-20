from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import os
import tempfile
from gtts import gTTS
import PyPDF2


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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)


app = Flask(__name__)

app.secret_key = b"NL[\xdb,\xb1\x80z\x94\xda\xe2\x99'~7\xda\xf8\x83\xc7\t\x15\x15\xf1<"
app.config['UPLOAD_FOLDER'] = 'uploaded_files'  # Specify your upload folder
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return 'No file part, Select PDF file only'

        file = request.files['pdf']
        if file.filename == '':
            return 'No selected file'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            save_filename = filename.split('.')[0]
            text = extract_text_from_pdf(file_path)
            speech_file_path = "mp3files/" + save_filename + ".mp3"
            text_to_speech(text, speech_file_path)

            return redirect('/')
        else:
            flash("Please select Acceptable file type (.pdf)")
            return redirect(request.url)

    return render_template('upload.html')


@app.route('/about')
def about():
    flash("WELCOME TO ABOUT PAGE", "success")
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission (e.g., save data to database or send email)
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
    app.run(debug=True)
