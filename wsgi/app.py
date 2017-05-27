import network_processor
import file_processor
import data_cleaner
import excelify
import os
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.environ['OPENSHIFT_DATA_DIR'] + '/txt_files'
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
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    else:
        return 'NOT ALLOWED !'

app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    app.run(debug=True)  # TODO: Remember to shut this off
