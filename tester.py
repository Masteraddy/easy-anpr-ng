import cv2
import numpy as np
import easyocr
import string
from numpy.lib.function_base import append

im_1_path = 'images/car5.jpg'
# im_1_path = 'uploads/faces/Steve_Jobs.jpg'

import os, os.path

def filter_plrec(results):
    plate = []
    dim = []
    for result in results:
        width = np.sum(np.subtract(result[0][1], result[0][0]))
        height = np.sum(np.subtract(result[0][2], result[0][1]))

        if width>height:
            dim.append(height)
            plate.append(result)

        print(height, width)

    maxindex = dim.index(max(dim))
    return plate[maxindex]


# Each face is tuple of (Name,sample image)    
known_faces = [('Obama','sample_images/obama.jpg'),
               ('Peter','sample_images/peter.jpg'),
              ]

# imgs = []
# path = "uploads/faces"
# valid_images = [".jpg",".gif",".png",".tga"]
# for f in os.listdir(path):
#     nm = os.path.splitext(f)[0]
#     ext = os.path.splitext(f)[1]
#     imgs.append((nm, path+'/'+f))
# print(imgs)

test = 'RBC587M'
PLATE_FOLDER = 'uploads/plates'

# def find_plate(file):
#     """
#     Return name for a known face, otherwise return 'Unknown'.
#     """
#     plates = []
#     for f in os.listdir(PLATE_FOLDER):
#         nm = os.path.splitext(f)[0]
#         plates.append((nm, os.path.join(PLATE_FOLDER, f)))
    
#     print(plates)
        
#     for name, path in plates:
#         if name==file:
#             return path
#     return 'Unknown' 

# print(find_plate(test))
    
def overlay_ocr_text(img_path, result, newname):
    '''loads an image, recognizes text, and overlays the text on the image.'''
    
    # loads image
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # recognize text
    ret = result
    # if OCR prob is over 0.5, overlay bounding box and text
    (bbox, text, prob) = ret
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = (int(top_left[0]), int(top_left[1]))
    bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
    
    cv2.rectangle(img=img, pt1=top_left, pt2=bottom_right, color=(255, 0, 0), thickness=10)
            
    # put recognized text
    platenumber = text.translate({ord(c): None for c in string.whitespace})
    print(f'Plate number: {platenumber}')
    cv2.putText(img=img, text=text, org=(top_left[0], top_left[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=8)
    # show and save image
            
    saved_plate = os.path.join(PLATE_FOLDER, newname)
    print(saved_plate)
    # cv2.imwrite(saved_plate, img)


def recognize_text(img_path):
    '''loads an image and recognizes text.'''
    
    reader = easyocr.Reader(['en'])
    return reader.readtext(img_path)


result = recognize_text(im_1_path)
plate = filter_plrec(result)

print(overlay_ocr_text(im_1_path, plate, 'newname'))
