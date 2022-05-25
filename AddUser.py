import pymongo
#import face_recognition
import cv2
import numpy as np
import Face

myclient = pymongo.MongoClient("mongodb://localhost:20000/")
mydb = myclient["voting"]
mycol = mydb["voting"]
def addVoter(name,password,id):
    for x in mycol.find({"id":id}):
        return("Voter Already Exists")
    x = mycol.insert_one({"name":name,"password":password,"id":id,"vote":"0"})
    Face.addUserFace(id)
    return("Done")

def AllVoters():
    for x in mycol.find():
        print(x)

def VerifyUser(id,password):
    for x in mycol.find({"id":id}):
        if(x["password"]==password):
            status = Face.VerifyUser(id)
            return(status)
        else:
            status = "Incorrect Credentials"
        return(status)
    return("Voter not registered")
def AddVote(id,party):
    for x in mycol.find({"id":id}):
        print(x)
        if(x["vote"] != "0"):
            return "Already Casted"
        else:
            mycol.update_one(x,{"$set":{"vote":party}})
            return("Added your vote")

def clearDb():
    r = mycol.delete_many({})
    Face.DeleteFaces()
    return("Database has been cleared, A new admin needs to be registered first !")

def result():
    votes={"A":0,"B":0,"C":0,"D":0}
    vote = ""
    for x in mycol.find({}):
        vote = str(x["vote"])
        print(vote)
        if(x["id"]=="0000"):
            continue
        else:
            if(vote!="0"):
                votes[vote]+=1
    return(votes)