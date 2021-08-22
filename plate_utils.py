import numpy as np
import easyocr
import os
import cv2
import string


PLATE_FOLDER = 'static/plates'
PROCESSING_FOLDER = 'static/processing'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

import time

def filter_plrec(results):
    plate = []
    dim = []
    for result in results:
        width = np.sum(np.subtract(result[0][1], result[0][0]))
        height = np.sum(np.subtract(result[0][2], result[0][1]))

        if width>height:
            dim.append(height)
            plate.append(result)

    maxindex = dim.index(max(dim))
    return plate[maxindex]

def overlay_ocr_text(img_path, result, newname):
    '''loads an image, recognizes text, and overlays the text on the image.'''
    
    # loads image
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # recognize text
    ret = result
    (bbox, text, prob) = ret
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = (int(top_left[0]), int(top_left[1]))
    bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
    
    cv2.rectangle(img=img, pt1=top_left, pt2=bottom_right, color=(255, 0, 0), thickness=4)
            
    # put recognized text
    platenumber = text.translate({ord(c): None for c in string.whitespace})
    print(f'Plate number: {platenumber}')
    cv2.putText(img=img, text=text, org=(top_left[0], top_left[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=8)
    
    # show and save image        
    saved_plate = os.path.join(PLATE_FOLDER, newname)
    cv2.imwrite(saved_plate, img)

def recognize_text(img_path):
    '''loads an image and recognizes text.'''
    
    start_time = time.time()
    reader = easyocr.Reader(['en'], gpu=True)
    res = reader.readtext(img_path)
    print("--- %s seconds ---" % (time.time() - start_time))
    return res

def find_plate(file):
    """
    Return name for a known face, otherwise return 'Unknown'.
    """
    plates = []
    for f in os.listdir(PLATE_FOLDER):
        nm = os.path.splitext(f)[0]
        plates.append((nm, os.path.join(PLATE_FOLDER, f)))
 
    for name, path in plates:
        if name==file:
            return path
    return 'Unknown' 
