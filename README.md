# PDF-text-to-speech-reader

This is a web application that allows users to upload PDF documents and converts the text to audio (MP3) using text-to-speech technology. Developed by TechLegion.

## Features
- Upload PDF files and convert them to speech (MP3)
- Supports multiple languages and accents
- Downloadable audio files for offline use
- User-friendly web interface
- Stores uploaded file info in MongoDB

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- MongoDB (running locally on default port 27017)

### Installation
1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd PDF-text-to-speech-reader/PDF-TTS-CONVERTER
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure MongoDB is running locally.

### Running the App
```bash
python app.py
```
The app will be available at `http://localhost:5000` by default.

## Usage
- Go to the Upload page, select a PDF, choose a language, and upload.
- Download or play the generated MP3 file.

## Troubleshooting
- **MongoDB connection errors:** Ensure MongoDB is running on `localhost:27017`.
- **File upload issues:** Only PDF files are accepted. Check file size and format.
- **Audio not generated:** Ensure you have an internet connection (gTTS uses Google APIs).

## License
MIT License

---
Developed by TechLegion
