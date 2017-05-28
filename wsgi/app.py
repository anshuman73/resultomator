import file_processor
import data_cleaner
import excelify
import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.environ['OPENSHIFT_DATA_DIR'] + 'txt_files'
ALLOWED_EXTENSIONS = ['txt']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def form():
    return render_template('base.html')


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        # results = request.form.to_dict()
        # file_processor.process(file_address)
        # return render_template("results.html", results=results)
        # check if the post request has the file part
        if 'file' not in request.files:
             return 'No file part'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_address = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_address)
            file_processor.process(file_address)
            data_cleaner.clean()
            excelify.excelify()
            return render_template('results.html')
        else:
            return 'Not a .txt file'
    else:
        return 'NOT ALLOWED !'


@app.route('/download1', methods=['GET', 'POST'])
def download1():
    return send_from_directory(directory=os.environ['OPENSHIFT_DATA_DIR'], filename='All CBSE 12th results.xlsx')


@app.route('/download2', methods=['GET', 'POST'])
def download2():
    return send_from_directory(directory=os.environ['OPENSHIFT_DATA_DIR'], filename='CBSE 12th Subject-wise results.xlsx')


app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    app.run()  # TODO: Remember to shut this off
