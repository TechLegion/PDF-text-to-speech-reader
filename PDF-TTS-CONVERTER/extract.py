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


extracted_text = extract_text_from_pdf('pdf files/CMP 104 -Module 1.pdf')
print(extracted_text)


def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)


text_to_speech(extracted_text, output_file='output.mp3')


