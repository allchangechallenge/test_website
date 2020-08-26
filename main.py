try:
    import configparser
    from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, HTTPException, Query, Request, Response, Cookie
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from fastapi.responses import HTMLResponse
    import uvicorn
    import time
    from base64 import b64encode, b64decode
    from urllib.parse import unquote, quote 
    import os
    import datetime
    import bcrypt
    from PIL import Image
    import json
    import os
    import random
    from base64 import b64decode, b64encode
    import pandas as pd
    import numpy as np
except:
    print("install stuff")
    import os
    commands = ["pip install bcrypt", "pip install fastapi", "pip install uvicorn", "pip install pillow"]
    for command in commands:
        os.system(command)
    


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



import pymongo
import pickle

topic = "./chinlin圖片/詞彙心像作業/Group4/"
def getChineseNameDict():
    import pandas as pd
    df = pd.read_excel("./刺激編號.xlsx")
    chineseName = {}
    for key, name in zip(df.圖片檔名, df.詞彙心像作業對應名稱):
        chineseName[key] = name
    chineseName["prac_1_coin"] = "錢幣"
    chineseName["prac_2_frog"] = "青蛙"
    return chineseName
chineseName = getChineseNameDict()

class User:
    def __init__(self, userId, password, topic = topic):
        self.userId = userId
        self.password = password
        self.status = "just init"
        if self.initVerifyUser():
            self.topic = topic
            self.query = self.createTestQuery(topic)
            self.working = ""
            self.status = "just init"
        else:
            return {"error": "User Name Not Right"}
        
    def createTestQuery(self, topic):
        query = os.listdir("%s"%topic)
        query2 = query.copy()
        random.shuffle(query)
        random.shuffle(query2)
        query = query + query2
        query = query[0:300]
        query = ["../../練習階段/prac_1_coin.jpg", "../../練習階段/prac_2_frog.jpg"] + query
        return query
    
    def initVerifyUser(self):
        return True
    
    def verify(self, userId, password):
        return userId == self.userId and password == self.password

    def getNextImg(self):
        if self.status == "img just get":
            filename = self.working
        elif self.notFinishTest():
            filename = self.getNextImgFile()
        with open(filename, 'rb') as f:
            img_encode = b64encode(f.read())
            img_b64 = img_encode.decode()
        self.status = "img just get"
        return img_b64


    def getNextImgFile(self):
        if self.notFinishTest():
            self.working = topic + self.query.pop(0)
            return self.working
        else:
            return ""

    def notFinishTest(self):
        return len(self.query) != 0

    def dumpToPickle(self):
        import pickle
        with open('./userData/%s.pickle'%self.userId, 'wb') as f:
            pickle.dump(self, f)
            return True
        return False
    
    
    
    def dumpToDB(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["NameImage"]
        mycol = mydb["User"]
        self_pickled = pickle.dumps(self)
        
        myquery = { "userId": self.userId}
        newvalues = {"$set": {"pickled": self_pickled,}}
        result = mycol.update_one(myquery, newvalues)
        
        if result.raw_result["updatedExisting"] == False:
            #create new
            data = {
                "userId": self.userId,
                "pickled": self_pickled,
                "timeStamp": datetime.datetime.utcnow(),
            }
            x = mycol.insert_one(data) 
    
    def getWorkingImgName(self):
        loc = [i for i, letter in enumerate(self.working) if letter == "/"]
        return self.working[loc[-1]+1:].replace(".jpg", "")


"""def getUser(userId, userKey):
    with open('../data/userData/%s.pickle'%userId, 'rb') as file:
        out = pickle.load(file)"""

def getUser(userId, pw):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["NameImage"]
    mycol = mydb["User"]
    myquery = { "userId": userId } 
    mydoc = mycol.find(myquery)
    dataList = list(mydoc)
    if len(dataList) != 0:
        pickled = dataList[0]["pickled"]
        user = pickle.loads(pickled)
        return user
    else:
        print("create new user ", userId)
        return User(userId, pw)

@app.get("/api/login")
async def login(request: Request, userId: str = "", pw: str = ""):
    #Because we have to store the pw in dataset to provide to student...
    #so I do not use hash in this part.

    print(userId, pw)
    print(request.cookies.get("userID"))

    result = True #get Data of username pw pair
    if result == True:
        """try:
            open('../data/userData/%s.pickle'%userId, 'rb')
        except FileNotFoundError:
            user = User(userId, pw)
            with open('../data/userData/%s.pickle'%userId, 'wb') as f:
                pickle.dump(user, f)"""

        out = {"status": "login successful"}
    else:
        out = {"status": "login failed"}
    return out


@app.get("/api/getNextImg")
async def getNextImg(request: Request, text: str = "", ):
    pw = request.cookies.get("userPW")
    userID = request.cookies.get("userID")

    print(userID, pw)
    
    user = getUser(userID, pw)
    
    print(user.status)
    
    if user.verify(userID, pw) == False:
        return {"status": "user verify error"}
    
    if user.notFinishTest():
        picture = user.getNextImg()
        status = "get successful"
    else:
        picture = ""
        status = "no more image"

    imgName_encoded = b64encode(user.getWorkingImgName().encode()).decode()
    
    out = {"status": status,
           "pic_b64": picture,
           "timeout": 20,
           "imgId": imgName_encoded,
          }
    
    user.dumpToDB()
    
    return out
    
@app.get("/api/sendRecord")
async def sendRecord(request: Request, data: str = ""):
    data = json.loads(data)
    data["imgId"] = b64decode(data["imgId"].encode()).decode()
    print(data)
    pw = request.cookies.get("userPW")
    userID = request.cookies.get("userID")
    
    #verify User
    if True: 
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["NameImage"]
        mycol = mydb["data"]
        try: 
            imgRealName = chineseName[data["imgId"]]
        except KeyError:
            imgRealName = None
        
        dataOut = {
            "userId": data["userID"],
            "imgId": data["imgId"],
            "imgRealName": imgRealName,
            "imgName": data["imgName"],
            "imgFamiliar": data["imgFamiliar"],
            "timeCostInWatch": data["timeCostInWatch"],
            "timeCostInName": data["timeCostInName"],
            "timeCostInFamiliar": data["timeCostInFamiliar"],
            "timeStamp": datetime.datetime.utcnow()
        }
        print(dataOut)
        x = mycol.insert_one(dataOut) 
        
        user = getUser(userID, pw)
        user.status = "answered"
        user.dumpToDB()
        
        return {"status": "send success", "restTime" : 5}
    else:
        return {"status": "user verify error"}
    
@app.get("/")
async def defaultRoute(request: Request):
    content = """
<script>
    window.location.replace("./static/index_0818.html");
    </script>
"""
    return HTMLResponse(content=content, status_code=200)


from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

        
if __name__ == "__main__":
    print("Hi")
    #uvicorn.run(app, host="0.0.0.0", port=8080)