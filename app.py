from flask import Flask, render_template, request, redirect, url_for, flash
import os
import shutil
from werkzeug.utils import secure_filename
import subprocess

UPLOAD_FOLDER = './app/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret_key"

# Allowed file check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'folder' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['folder']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'presentation_folder')
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path)

        # Save the uploaded folder
        file.save(os.path.join(folder_path, filename))
        flash('Folder uploaded successfully')
        return redirect(url_for('play'))
    else:
        flash('Invalid file type')
        return redirect(request.url)

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/start_presentation', methods=['POST'])
def start_presentation():
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'presentation_folder')
    if os.path.exists(folder_path):
        # Run feature2.py using subprocess
        subprocess.Popen(['python', 'feature2.py'], cwd=os.getcwd())
        return "Presentation started in a new window. Close it to return."
    else:
        flash('No folder uploaded.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
