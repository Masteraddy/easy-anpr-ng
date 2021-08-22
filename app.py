from flask import Flask, request, redirect, render_template, flash, url_for

import os
import json
import string
from werkzeug.utils import secure_filename

import face_utils as fr
import plate_utils as pl


PLATE_FOLDER = 'static/plates'
FACE_FOLDER = 'static/faces'
PROCESSING_FOLDER = 'static/processing'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)

app.secret_key='secret123'

@app.route('/', methods=['POST', 'GET'])
def save_face_and_platenumber():
    if request.method == 'POST':
        # check if the post request has the file part
        if ('file1' not in request.files) or ('file2' not in request.files):
            flash('No file part')
            return redirect(request.url)

        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        # if user does not select file, browser also submit an empty part without filename
        if file1.filename == '' or file2.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if allowed_file(file1.filename) and allowed_file(file2.filename):
            plate_path = os.path.join(PROCESSING_FOLDER, secure_filename(file1.filename))
            face_path = os.path.join(PROCESSING_FOLDER, secure_filename(file2.filename))
            
            file1.save(plate_path)
            file2.save(face_path)
            ext1 = file1.filename.split('.')[1]
            ext2 = file2.filename.split('.')[1]

            print(plate_path, face_path)

            #Recognizing the text
            ret = pl.recognize_text(plate_path)
            #filter the plate number
            if len(ret) < 2:
                flash('Only picture with platenumber is allowed')
                return render_template('home.html',error="Only picture with platenumber is allowed")


            plateresult = pl.filter_plrec(ret)
            (dim, platetxt, probs) = plateresult
            platenumber = platetxt.translate({ord(c): None for c in string.whitespace}).upper()
            # platenumber = ret[2][1].translate({ord(c): None for c in string.whitespace})
            print(platenumber)
            # newresult = (ret[0], ret[2])
            newPltname = secure_filename(platenumber+'.'+ext1)

            #Detect the face on the picture
            face = fr.find_face_locations(face_path)
            if len(face) == 0:
                print(face)
                flash('No face or more than one face is found')
                return redirect(request.url)
            # print(newresult)

            #Rename the files into the platenumber
            saved_plate = os.path.join(PLATE_FOLDER, newPltname)
            saved_face = os.path.join(FACE_FOLDER, secure_filename(platenumber+'.'+ext2))

            #Draw a triangle around the plate and face
            pl.overlay_ocr_text(plate_path, plateresult, newPltname)
            fr.overlay_face(face_path, face, saved_face)

            # os.rename(plate_path, saved_plate)
            # os.rename(face_path, saved_face)
            os.remove(plate_path)
            os.remove(face_path)

            resp_data = {"plate_number": saved_plate, "owner_face": saved_face } # convert ret (numpy._bool) to bool for json.dumps

            return render_template('result.html', result=resp_data)

    # Return a demo page for GET request
    return render_template('home.html')


@app.route('/check-plate', methods=['POST', 'GET'])
def check_with_face():
    if request.method == 'POST':
        # check if the post request has the file part
        if ('file1' not in request.files):
            flash('No file part')
            return redirect(request.url)

        file1 = request.files.get('file1')
        # if user does not select file, browser also submit an empty part without filename
        if file1.filename == '':
            flash('No file is selected')
            return redirect(request.url)

        if allowed_file(file1.filename):
            result = fr.face_rec(file1)
            
            if result == 'No face is found':
                flash('No face is found')
                return redirect(request.url)

            plate = pl.find_plate(result)
            face = fr.find_face(result)
            
            if plate=='Unknown' or face=='Unknown':
                flash('This face is not found in our database')
                return redirect(request.url)

            resp_data = {"plate_number": plate, "owner_face": face } 

            return render_template('result.html', result=resp_data)

    # Return a demo page for GET request
    return render_template('check.html', page='Face', check="Plate Number")

@app.route('/check-face', methods=['POST', 'GET'])
def check_with_plate():
    if request.method == 'POST':
        # check if the post request has the file part
        if ('file1' not in request.files):
            flash('No file part')
            return redirect(request.url)

        file1 = request.files.get('file1')
        # if user does not select file, browser also submit an empty part without filename
        if file1.filename == '':
            flash('No file is selected')
            return redirect(request.url)

        if allowed_file(file1.filename):
            plate_path = os.path.join(PROCESSING_FOLDER, secure_filename(file1.filename))
            
            file1.save(plate_path)
            #Recognizing the text
            ret = pl.recognize_text(plate_path)
            #filter the plate number
            if len(ret) < 2 or not ret:
                flash('Only picture with platenumber is allowed')
                return redirect(request.url)

            plateresult = pl.filter_plrec(ret)
            (dim, platetxt, probs) = plateresult
            platenumber = platetxt.translate({ord(c): None for c in string.whitespace}).upper()

            print(platenumber)

            plate = pl.find_plate(platenumber)
            face = fr.find_face(platenumber)

            if plate=='Unknown' or face=='Unknown':
                flash('This platenumber is not in our database')
                return redirect(request.url)

            resp_data = {"plate_number": plate, "owner_face": face } 

            return render_template('result.html', result=resp_data)

    # Return a demo page for GET request
    return render_template('check.html', page='Plate Number', check="Face")

# Run in HTTP
# When debug = True, code is reloaded on the fly while saved
app.run(host='0.0.0.0', port='5000', debug=True)

# 1. Seperate face utils from plate utils
# 2. Design templates for user_interface e.g loading and different page for result
# 3. Show errors with flash instead of json