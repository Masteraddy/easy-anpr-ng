from flask import Flask, render_template, url_for, redirect
import os

app = Flask(__name__)

picFolder = os.path.join('uploads', 'processing')
print(picFolder)
app.config['UPLOAD_FOLDER'] = picFolder


@app.route("/")
def index():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'car1.jpg')
    return render_template("index.html", user_image=pic1)   


@app.route("/static/<path:filename>")
def display(filename):
    print(filename)
    return redirect(url_for('static', filename=filename))


app.run(host='0.0.0.0', port='8000', debug=True)