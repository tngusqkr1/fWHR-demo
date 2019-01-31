# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri
from .models import Image
import time
import os
import requests
import cv2
import dlib
from imutils import face_utils
from scipy import misc
import numpy as np

# Create your views here.
def main(request):
    return render(request, 'main.html', {})

def simple_upload(request):
    if request.method == 'POST':
        myfile = request.FILES['photo']

        myfile_name = iri_to_uri(myfile.name)
        gender = request.POST.getlist('gender')[0]
        age = int(request.POST.getlist('age')[0])
        country = request.POST.getlist('country')[0]

        fs = FileSystemStorage()

        filename = fs.save(myfile_name, myfile)
        uploaded_file_url = fs.url(filename)

        image = Image.objects.create()
        image.image = filename
        image.gender = gender
        image.age = age
        image.country = country
        # features = faceAPI(uploaded_file_url)
        l, f, fwhr_index = fWHR('media/'+filename)
        l = fs.url(l)[6:]
        f = fs.url(f)[6:]

        image.fwhr = fwhr_index
        image.save()

        return render(request, 'main.html', {
            'uploaded_file_url_no_media' : myfile.name,
            'uploaded_file_url': uploaded_file_url,
            'landmark_file_url' : l,
            'fWHR_file_url': f,
            'gender':gender,
            'age':age,
            'country':country,
            'fwhr_index': fwhr_index,

        })
    return render(request, 'main.html')

def image_download(request, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    return render(request, 'main.html')




def faceAPI(image_path):
    image_url = open(image_path,'rb').read()
    # ip = socket.gethostbyname(socket.gethostname())
    subscription_key = "f78920ca9b6242a9ad0fbd48b543ef42"
    assert subscription_key
    face_api_url = "https://eastasia.api.cognitive.microsoft.com/face/v1.0/detect"

    columns = ["SerialNum", "Age", "Gender", "Fear", "Sadness", "Disgust", "Contempt", "Neutral", "Happiness", "Anger",
               "Glasses", "Moustache", "Beard", "Sideburns", "Bald"]


    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}

    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur',
    }

    response = requests.post(face_api_url, params=params, headers=headers, data=image_url)

    faces = response.json()
    f = {}

    try:
        features = faces[0]["faceAttributes"]
        f = {"Age": features["age"], "Gender": features['gender'],
             "Fear": features["emotion"]["fear"], "Sadness": features["emotion"]["sadness"],
             "Disgust": features["emotion"]["disgust"],
             "Contempt": features["emotion"]["contempt"], "Neutral": features["emotion"]["neutral"],
             "Happiness": features["emotion"]["happiness"],
             "Anger": features["emotion"]["anger"],
             "Glasses": features["glasses"],
             "Moustache": features["facialHair"]["moustache"], "Beard": features["facialHair"]["beard"],
             "Sideburns": features["facialHair"]["sideburns"],
             "Bald": features["hair"]["bald"]}

    except:
        pass

    return f


def fWHR(image_url):
    image = misc.imread(image_url)

    print("loaded image")

    gray = misc.imread(image_url, mode="L")
    detector = dlib.get_frontal_face_detector()
    rects = detector(gray, 1)
    rect = rects[0]

    # pre-trained shape predictor's path
    shape_predictor_path = "media/pretrained/shape_predictor_68_face_landmarks.dat"

    predictor = dlib.shape_predictor(shape_predictor_path)

    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)
    # print(shape)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    img_lmrk = image.__copy__()
    for i, sh in enumerate(shape):
        if i in [1, 15, 21, 22, 51]:
            cv2.circle(img_lmrk, (sh[0], sh[1]), 2, (0, 0, 255), 3)
        cv2.circle(img_lmrk, (sh[0], sh[1]), 1, (0, 0, 255), 2)


    cv2.rectangle(image, (shape[1][0], (shape[21][1] + shape[22][1]) // 2), (shape[15][0], shape[51][1]),
                  (0, 0, 255), 3)

    landmark_image_path = "".join(image_url.split(".")[:-1]) + "_landmarks.jpg"
    fwhr_image_path = "".join(image_url.split(".")[:-1]) + "_fwhr.jpg"

    cv2.imwrite(landmark_image_path, img_lmrk)
    cv2.imwrite(fwhr_image_path, image)

    width = ((shape[0][0] - shape[15][0]) ** 2 +
         (shape[0][1] - shape[15][1]) ** 2) ** (0.5)

    avg_21_22 = (shape[21] + shape[22]) / 2.0
    height = ((avg_21_22[0] - shape[51][0]) ** 2 +
          (avg_21_22[1] - shape[51][1]) ** 2) ** (0.5)

    fwhr_index = width / height
    # print(fwhr_index)

    return landmark_image_path, fwhr_image_path, fwhr_index
