#creating database
import cv2, sys, numpy, os
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'  #All the faces data will be present this folder
#import face_recognition
import shutil
import boto3

def addUserFace(name):
    sub_data = name
    path = os.path.join(datasets, sub_data)
    if not os.path.isdir(path):
        os.mkdir(path)
    (width, height) = (130, 100)    # defining the size of image
    face_cascade = cv2.CascadeClassifier(haar_file)
    webcam = cv2.VideoCapture(0) #'0' is use for my webcam, if you've any other camera attached use '1' like this

    # The program loops until it has 30 images of the face.
    count = 1
    (_, im) = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 4)
    cv2.imwrite('%s/%s.jpg' % (path,count), im)
    webcam.release()

def VerifyUser(name):
    sub_data = name 
    print(name)   
    path = os.path.join(datasets, sub_data)
    database = path+"/1.jpg"
    """
    known = face_recognition.face_encodings(image)[0]
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    try:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encoding = face_recognition.face_encodings(rgb_small_frame, face_locations)
        matches = face_recognition.compare_faces(known, face_encoding)
        if(matches[0]==True):
            print(matches[0])
            print("Face recognised")
            return 1
        else:
            print("Face Not Recognised")
            return("Face Not Recognised")
    except:
        return "Face Not Found"
    """
    client = boto3.client('rekognition',region_name='us-east-1',aws_access_key_id = "AKIAZLENVOE55T4ZCSSE",aws_secret_access_key="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")
    cap = cv2.VideoCapture(0)
    ret, webcam = cap.read()
    cv2.imwrite(datasets+"/a.jpg",webcam)
    webcam = datasets+"/a.jpg"
    with open(database,"rb") as source_image:
        b1 = source_image.read()
    with open(webcam,"rb") as source_image:
        b2 = source_image.read()
    try:
        response = client.compare_faces(SourceImage={'Bytes' : b1},TargetImage={"Bytes": b2},SimilarityThreshold=80)
        if(len(response["FaceMatches"])!=0):
            print("Face Recognised")
            return(1)
        else:
            print("Face Not Recognised")
            return("Face Not Recognised")
    except:
        return "Face Not Found"

def DeleteFaces():
    shutil.rmtree(datasets)
    os.mkdir("datasets")