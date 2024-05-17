from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os
from flask import render_template
from pdf2docx import Converter
from docx import Document
from flask import Flask, render_template, request, send_file
from pytube import YouTube
from moviepy.editor import AudioFileClip
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DATABASE = 'users.db'
uploads_dir = os.path.join(os.getcwd(), 'uploads')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                        )''')
        db.commit()
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

def is_khmer(char):
    # Unicode range for Khmer script
    khmer_unicode_range = (0x1780, 0x17FF)  # Update this range as needed

    # Check if the character code falls within the Khmer Unicode range
    return khmer_unicode_range[0] <= ord(char) <= khmer_unicode_range[1]

def contains_khmer(text):
    return any(is_khmer(char) for char in text)

def convert_pdf_to_word(pdf_file):
    word_output_path = os.path.join('static', 'output.docx')

    # Convert PDF to Word using pdf2docx
    cv = Converter(pdf_file)
    cv.convert(word_output_path, start=0, end=None)
    cv.close()

    return word_output_path

def extract_text_from_word(word_file):
    doc = Document(word_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

@app.route('/show_users')
def show_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users''')
    users = cursor.fetchall()
    conn.close()
    return render_template('show_users.html', users=users)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    
    return render_template('index.html')
@app.route('/home')
def home():
    images = ['image1.jpg', 'image2.jpg', 'image3.jpg']  # Replace with your image paths
    return render_template('home.html', images=images)

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/pdfconverter')
def pdfconverter():
    return render_template('pdfconverter.html')

@app.route('/youtubeconverter')
def youtubeconverter():
    return render_template('youtubeconverter.html')

@app.route('/videoconverter')
def videoconverter():
    return render_template('videoconverter.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM users WHERE username=? AND password=?''', (username, password))
    user = cursor.fetchone()
    if user:
        return redirect(url_for('home'))
    else:
        return "Login failed. Invalid username or password."

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            error = "Passwords do not match. Please try again."
        else:
            db = get_db()
            cursor = db.cursor()
            try:
                cursor.execute('''INSERT INTO users (username, password) VALUES (?, ?)''', (username, password))
                db.commit()
                return redirect(url_for('home'))
            except sqlite3.IntegrityError:
                error = "Username already exists. Please choose a different one."
    return render_template('register.html', error=error)

@app.route('/success')
def success():
    return "Login or registration successful. You are now redirected to the success page."

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdfFile' not in request.files:
        return "No PDF file provided."

    pdf_file = request.files['pdfFile']

    if pdf_file.filename == '':
        return "No selected file."

    pdf_file_path = os.path.join('uploads', pdf_file.filename)
    pdf_file.save(pdf_file_path)

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        # Check if the PDF contains Khmer characters
        pdf_text = extract_text_from_word(convert_pdf_to_word(pdf_file_path))
        if contains_khmer(pdf_text):
            return "The PDF contains Khmer characters. Conversion not supported."
        
        # Convert PDF to Word
        word_output_path = convert_pdf_to_word(pdf_file_path)

        # Remove the uploaded PDF after processing
        os.remove(pdf_file_path)

        return f"Conversion successful! <a href='/download'>Download Word Document</a>"
    else:
        return "Invalid file format. Please upload a PDF file."

@app.route('/download')
def download():
    path = os.path.join('static', 'output.docx')
    return send_file(path, as_attachment=True)

@app.route('/redirect-to-target')
def redirect_to_target():
    return redirect(url_for('pdfconverter'))

@app.route('/redirect-to-target1')
def redirect_to_target1():
    return redirect(url_for('youtubeconverter'))

@app.route('/redirect-to-target2')
def redirect_to_target2():
    return redirect(url_for('videoconverter'))

@app.route('/download1', methods=['POST'])
def download1():
    url = request.form['url']
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(filename='video')
        return send_file('video.mp4', as_attachment=True)
    except Exception as e:
        return str(e)

@app.route('/convert1', methods=['POST'])
def convert1():
    url = request.form['url']
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        stream.download(filename='audio')
        audio_clip = AudioFileClip('audio.mp4')
        audio_clip.write_audiofile('audio.mp3')
        return send_file('audio.mp3', as_attachment=True)
    except Exception as e:
        return str(e)
    
@app.route('/convert2', methods=['POST'])
def convert2():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file.save(filename)
        try:
            clip = VideoFileClip(filename)
            mp4_filename = filename.split('.')[0] + '.mp4'
            clip.write_videofile(mp4_filename)
            return f'Video successfully converted to MP4: <a href="{mp4_filename}">{mp4_filename}</a>'
        except Exception as e:
            return f'An error occurred during conversion: {str(e)}'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
