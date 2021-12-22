from flask import Flask, request, redirect, render_template, flash, url_for
from flask_mongoengine import MongoEngine
from dotenv import load_dotenv


import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url

import os
import json
import string
from datetime import date
from werkzeug.utils import secure_filename

import face_utils as fr
import plate_utils as pl
import dbconfig as db

load_dotenv()

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
    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'), api_key=os.getenv('API_KEY'), 
    api_secret=os.getenv('API_SECRET'))

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

            usernotcheck = db.UserData.objects(platenumber=platenumber, ischeck=False).first();
            # print(usernotcheck)
            if(usernotcheck):
                return redirect("/result/"+usernotcheck.id)

            #Detect the face on the picture
            face = fr.find_face_locations(face_path)
            if len(face) == 0:
                print(face)
                flash('No face or more than one face is found')
                return redirect(request.url)

            #Rename the files into the platenumber
            saved_plate = os.path.join(PLATE_FOLDER, newPltname)
            saved_face = os.path.join(FACE_FOLDER, secure_filename(platenumber+'.'+ext2))

            #Draw a triangle around the plate and face
            pl_img = pl.overlay_ocr_text(plate_path, plateresult, newPltname)
            fr_img = fr.overlay_face(face_path, face, saved_face)

            print(pl_img)
            print(fr_img)

            pl_result = cloudinary.uploader.upload(pl_img)
            fr_result = cloudinary.uploader.upload(fr_img)

            print(pl_result)
            print(fr_result)

            # os.rename(plate_path, saved_plate)
            # os.rename(face_path, saved_face)
            os.remove(plate_path)
            os.remove(face_path)

            resp_data = {"plate_number": pl_result.get('secure_url'), "owner_face": fr_result.get('secure_url') } # convert ret (numpy._bool) to bool for json.dumps
            newdata = db.UserData(face=fr_result.get('secure_url'), plate=pl_result.get('secure_url'), platenumber=platenumber, ischeck=False, checkintime=date.today())
            newdata.save()

            return render_template('regresult.html', result=resp_data)

    # Return a demo page for GET request
    return render_template('home.html')

#Just for testing
@app.route('/check', methods=['GET'])
def check_e():
    usernotcheck = db.UserData.objects(platenumber="RBC587MK", ischeck=False).first();
    print(usernotcheck.platenumber, usernotcheck.ischeck, usernotcheck.id)

    if(usernotcheck):
        usercheck = db.UserData.objects(platenumber="RBC587MK").all();
        allchecks = usercheck.to_json()
        
        print(usernotcheck.to_json())
        usernot = {"plate_number": usernotcheck.plate, "owner_face": usernotcheck.face }
        return render_template('result.html', result=usernot, allchecks=allchecks)

    flash('Platenumber is not found in the database')
    return redirect('/')


#Update The isCheck and checkout time
@app.route('/checkout/<id>', methods=['POST'])
def check_out(id: str):
    # body = request.get_json();
    ud = db.UserData.objects.get_or_404(id=id);
    ud.update(checkouttime=date.today(), ischeck=True)
    print(ud.to_json());
    return redirect("/plate/"+ud.platenumber)


@app.route('/plate/<plate>', methods=['POST', 'GET'])
def check_plate(plate: str):
    usernotcheck = db.UserData.objects(platenumber=plate).first();

    if(usernotcheck):
        usercheck = db.UserData.objects(platenumber=plate).all();
        allchecks = usercheck.to_json()
        print(allchecks)
        return render_template('result.html', result=usernotcheck, allchecks=usercheck)

    flash('Platenumber is not found in the database')
    return redirect('/')

@app.route('/check-with-face', methods=['POST', 'GET'])
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

            if result == "Unknown":
                flash('This face is not found in our database')
                return redirect(request.url)

            # Find the platenumber from the database
            return redirect("/plate/"+result)
            
    # Return a demo page for GET request
    return render_template('check.html', page='Face', check="With Face")

@app.route('/check-with-plate', methods=['POST', 'GET'])
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

            reslt = db.UserData.objects(platenumber=platenumber).first();

            if reslt:
                # Find the platenumber from the database
                return redirect("/plate/"+reslt.platenumber)

            flash('This platenumber is not in our database')
            return redirect(request.url)

    # Return a demo page for GET request
    return render_template('check.html', page='Plate Number', check="With Plate Number")

# Run in HTTP
# When debug = True, code is reloaded on the fly while saved
app.run(host='0.0.0.0', port='5000', debug=False)

# 1. Seperate face utils from plate utils
# 2. Design templates for user_interface e.g loading and different page for result
# 3. Show errors with flash instead of json
