from wsgi import network_processor
from wsgi import file_processor
from wsgi import data_cleaner
from wsgi import excelify

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def form():
    return render_template('base.html')


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        results = request.form.to_dict()
        file_processor.process(file_address)
        return render_template("results.html", results=results)
    else:
        return 'NOT ALLOWED !'

if __name__ == '__main__':
    app.run(debug=True)  # TODO: Remember to shut this off
