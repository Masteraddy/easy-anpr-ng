import numpy as np
import os
from PIL import Image, ImageDraw
from werkzeug.utils import secure_filename
import face_recognition as fr


FACE_FOLDER = 'static/faces'
PROCESSING_FOLDER = 'static/processing'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


def find_face(file):
    """
    Return name for a known face, otherwise return 'Unknown'.
    """
    faces = []
    for f in os.listdir(FACE_FOLDER):
        nm = os.path.splitext(f)[0]
        faces.append((nm, os.path.join(FACE_FOLDER, f)))
        
    for name, path in faces:
        if name==file:
            return path
    return 'Unknown' 

def compare_faces(file1, file2):
    """
    Compare two images and return True / False for matching.
    """
    # Load the jpg files into numpy arrays
    image1 = fr.load_image_file(file1)
    image2 = fr.load_image_file(file2)
    
    # Get the face encodings for each face in each image file
    # Assume there is only 1 face in each image, so get 1st face of an image.
    image1_encoding = fr.face_encodings(image1)[0]
    image2_encoding = fr.face_encodings(image2)[0]
    
    # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
    results = fr.compare_faces([image1_encoding], image2_encoding)    
    return results[0]



def face_rec(file):
    """
    Return name for a known face, otherwise return 'Unknown'.
    """
    known_faces = []

    faces = find_face_locations(file)
    if len(faces) == 0:
        print(faces)
        return 'No face is found'

    for f in os.listdir(FACE_FOLDER):
        nm = os.path.splitext(f)[0]
        # ext = os.path.splitext(f)[1]
        known_faces.append((nm, os.path.join(FACE_FOLDER, secure_filename(f))))
        
    for name, known_file in known_faces:
        if compare_faces(known_file,file):
            return name
    return 'Unknown' 

def find_face_locations(file):
    # Load the jpg file into a numpy array
    image = fr.load_image_file(file)

    # Find all face locations for the faces in the image
    face_locations = fr.face_locations(image)
    
    # return facial features if there is only 1 face in the image
    print(face_locations)
    if len(face_locations) != 1:
        return ()
    else:
        return face_locations[0]  

def overlay_face(file, face, name):
    image = fr.load_image_file(file)
    # Convert to PIL format
    pil_image = Image.fromarray(image)
    (top, right, bottom, left) = face
    # Create a ImageDraw instance
    draw = ImageDraw.Draw(pil_image)
    draw.rectangle(((left, top), (right, bottom)), outline=(255,0,0))

    pil_image.save(name)

    del draw