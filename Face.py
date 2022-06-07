#creating database
import cv2, os
haar_file = 'C:/Users/chuch/anaconda3/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml'
datasets = 'Face'  #All the faces data will be present this folder
#import face_recognition
import shutil
import boto3

def addUserFace(id):
    sub_data = id
    path = os.path.join(datasets, sub_data)
    if not os.path.isdir(path):
        os.mkdir(path)
    (width, height) = (130, 100)    
    face_cascade = cv2.CascadeClassifier(haar_file)
    webcam = cv2.VideoCapture(0) 

    count = 1
    try:
        (_, im) = webcam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 4)
        cv2.imwrite('%s/%s.jpg' % (path,count), im)
        webcam.release()
    except:
        return "Open your Camera"
    return "Correct"

def VerifyUser(id):
    sub_data = id 
    path = os.path.join(datasets, sub_data)
    database = path+"/1.jpg"
    client = boto3.client('rekognition',region_name='us-east-1',aws_access_key_id = "Access key id",aws_secret_access_key="access key")
    cap = cv2.VideoCapture(0)
    try:
        ret, webcam = cap.read()
        cv2.imwrite(datasets+"/a.jpg",webcam)
        webcam = datasets+"/a.jpg"
    except:
        return "Please Open The Camera"
    with open(database,"rb") as source_image:
        b1 = source_image.read()
    with open(webcam,"rb") as source_image:
        b2 = source_image.read()
    try:
        response = client.compare_faces(SourceImage={'Bytes' : b1},TargetImage={"Bytes": b2},SimilarityThreshold=80)
        if(len(response["FaceMatches"])!=0):
            return "Correct"
        else:
            return "Face Not Recognised"
    except:
        return "Face Not Found"

def DeleteFaces():
    shutil.rmtree(datasets)
    os.mkdir("Face")