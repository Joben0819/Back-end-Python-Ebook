# import sys
from fastapi import Depends, FastAPI, File, UploadFile, Form, HTTPException, Depends
from pymongo import MongoClient
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pathlib import Path
import os
import io
import random
import base64
from fastapi.middleware.cors import CORSMiddleware
import jwt
from bson import ObjectId

Port = 8000
Domain = 'http://localhost:8000'
SECRET_KEY = "4"

def create_token(data: dict, secret:str, expires_delta: int):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str, secret:str):
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.DecodeError:
        return {"error": "Invalid token"}

user_data = {"sub": "Joben"}
token = create_token(user_data, secret="3", expires_delta=3600)  
decoded_token = decode_token(token, secret="3")
# print(decoded_token, 'ss')

def print_and_increment():
    if not hasattr(print_and_increment, 'counter'):
        print_and_increment.counter = 1
    else:
        print_and_increment.counter += 1

    return print_and_increment.counter

# print_and_increment() 


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

client = MongoClient("mongodb+srv://Joben:Anne060123@joben.a1aoz0g.mongodb.net/?retryWrites=true&w=majority")
db = client["Users"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Register(BaseModel):
    name: str
    password: str
class Login(BaseModel):
    name: str
    password: str
class FolderInput(BaseModel):
    title: str
    base64img: str
    id: int
    
class TextFileInput(BaseModel):
    file_name: str  
    text_content: str  
    Book: str  
class Contents(BaseModel):
    num: str
    Book: str
    
class Process(BaseModel):
    id: int
    book: str
    
class Onrating(BaseModel):
    id: int
    book: str
    username: str
    reader:int

class rates(BaseModel):
    id: int
    name: str
    book: str
    
class Addbook(BaseModel):
    id: int
    book: str
    image: str
    name: str
    idx: int
class Onread(BaseModel):
    id: int
    book: str
    image: str
    name: str
    idx: int
    inread: int
    author: str
    
class Writers(BaseModel):
    id: int
    username: str
    address: str
    Fullname: str
    Phonenumber: str
    status: int

class Stories(BaseModel):
    id: int
    book: str
    
class Author(BaseModel):
    username: str
class Removebook(BaseModel):
    id: int
    book: str
    name: str
class AddbookData(BaseModel):
    name: str
    id: int
    
@app.post("/register/")
async def create_item(data: Register):
    key = f'{print_and_increment()}'
    name = data.name
    password = data.password
    collection = db.get_collection("Users")
    data2 = list(collection.find({}))
    data3 = list(collection.find({ "name": name, "password": password}))
    
    for item in data2:
        item["_id"] = str(item["_id"])  
        
    for item in data3:
        item["_id"] = str(item["_id"]) 
        
    if(name == "" or password == "" ):
        error_message = "null"
        return JSONResponse(content={"message": error_message}, status_code=200)
    
    elif data3:
        return JSONResponse(content={"message": "null"}, status_code=200)
    
    elif( data3 == []):
        length = len(data2)
        collection.insert_one({"name": name , "password": password , "id": data2[length -1 ].get("id") + 1})
        data4 = list(collection.find({ "name": name, "password": password}))
        for item in data4:
            item["_id"] = str(item["_id"])  
        return data4
  
@app.post("/login")
async def create_item(data: Login):
    collection = db["Users"]
    password = data.password
    name = data.name
    data2 = list(collection.find({"name": name, "password": password}))
    
    if data2 == []:
        return JSONResponse(status_code=200,content={"detail": "Not existed"})
    for item in data2:
        item["_id"] = str(item["_id"])  
    return data2[0]

@app.get("/get_data/")
async def get_data():
    collection = db["Ebooks"]
    data = list(collection.find({}))
    
    if data == []: 
        return {"detail":"wala"}
    for item in data:
        item["_id"] = str(item["_id"])
        item.pop("content", None)

    return JSONResponse(content=data)

@app.get("/get_user_data/")
async def get_data():
    collection = db["Users"]
    data = list(collection.find({}))
    data1 = len(data)
    for item in data:
        item["_id"] = str(item["_id"])  
    return data[data1 - 1]

@app.post("/Added_books/")
async def get_data(data: AddbookData):
    collection = db["Addbook"]
    name = data.name
    if name is None :
        return {"data": "None"}
    else:
        data2 = list(collection.find({"id": data.id}))
        if data2 == []:
            return {"data": "None"}
        else:
            for item in data2:
                item["_id"] = str(item["_id"])  
            return data2


@app.post("/create_folder/")
async def create_folder(folder_name: FolderInput):
    # new_folder_path = f"./Ebooks/{folder_name.title}"
    collection = db.get_collection("Ebooks")
    data1 = list(collection.find({"title": folder_name.title}))
    for item in data1:
        item["_id"] = str(item["_id"]) 
    # new_directory = Path(new_folder_path)
    # new_directory.mkdir(parents=True, exist_ok=True) hello world

    if data1 == []:
        collection.insert_one({"title": folder_name.title, "image": folder_name.base64img, "id": folder_name.id,  })
        return {"message": f"Folder '{folder_name.title}' created successfully."}
    
    else:
        return {"message": f"Folder '{folder_name.title}' already exists."}

@app.post("/create_text_file/")
async def create_text_file(text_data: TextFileInput):
    file_name = text_data.file_name
    text_content = text_data.text_content
    Book_store = text_data.Book
    collection = db.get_collection("Ebooks")
    existing_user = collection.find_one({"filename": Book_store})
    existing_data = collection.find_one({"chapter.title": file_name ,"filename": Book_store })
    if existing_user is None:
        return { "status": False, "Message": "Wrong Data"}
    
    if existing_data:       
        collection.update_one(
            {"filename": Book_store, "chapter.title": file_name },
            {"$set": {"chapter.$.title": file_name , "chapter.$.content": text_content  }}
        )            
        return{"status": "Added"}
    
    collection.update_one(
    {"filename": Book_store},
    {"$push": {"chapter": { "title" : file_name, "content": text_content}}}
    )
    return {"status": "Added"}

@app.post("/UploadFile/")
async def create_upload_file(file: UploadFile = File(...), filename: str = Form(...), Author1: str = Form(...), Id: str = Form(...)):
    collection = db.get_collection("Ebooks")
    result = collection.find_one({"filename": filename})
    
    if result:
        collection.insert_one({"filename": filename, "content": file.file.read(), "image": f"{Domain}/get_image/{filename}", "id": Id , "author": Author1, "reader": 0 , "rating": 0  })
        return {"detail": "Edited the Chapter"}
    
    else:
        # data2 = list(collection.find({}))
        # for item in data2:
        #     item["_id"] = str(item["_id"]) 
        # setid = len(data2)
        collection.insert_one({"filename": filename, "content": file.file.read(), "image": f"{Domain}/get_image/{filename}", "id": Id , "author": Author1, "reader": 0 , "rating": 0  })
        return{"detail": "Added"}
    
@app.post('/YourBook')
async def writer(data: Stories):
    collection = db['Writer']
    data1 = collection.find_one({"id": data.id})
    
    if data1:
        collection.update_one(
            {"id": data.id},
            {"$push": {"YourBook":{"bookshelf": data.book, "reader": 0, "rating": 0}}})
    else:    
        return{"detail": "Nodata"}  

# def get_file_content(file_id: str):
#     collection = db.get_collection("Ebooks")
#     result = collection.find_one({"filename": file_id})
#     if result:
#         return result["content"]
#     else:
#         raise HTTPException(status_code=404, detail="File not found")

@app.get("/get_image/{file_id}")
async def get_image(file_id: str):
    collection = db.get_collection("Ebooks")
    result = collection.find_one({"filename": file_id})
    if result:
        content = result.get("content")
        return StreamingResponse(io.BytesIO(content), media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Image not found")


# @app.post("/read_file/")
# def read_root(data: Contents):
#     num = data.num
#     book = data.Book
#     file_path = f"./Ebooks/{book}/{num}"

#     if not os.path.exists(file_path):
#         return {"error": "File not found"}

#     try:
#         with open(file_path, "r", encoding="utf-8") as file:
#             file_content = file.read()
#         return {"message": file_content}
    
#     except Exception as e:  
#         with open(file_path, "r") as file:
#             file_content = file.read()
#         return {"message": file_content}
    
@app.post("/add_book/")
async def read_root(data: Addbook):
    collection = db.get_collection("Addbook")
    existing_user = collection.find_one({"id": data.id})
    existing_data = list(collection.find({"Books.book": data.book, "id": data.id}))   
    for item in existing_data:
        item["_id"] = str(item["_id"])  
    if existing_data == []:
        if existing_user:
            existing_datas = list(collection.find({"Books.book": data.book, "id": data.id,"Books.status": 2 }))   
            if existing_datas:
                collection.update_one(
                {"id": data.id, "Books.book": data.book},
                {"$set": {"Books.$.status": 1  }}
                )
                return{"detail": "Added but status 2 to be status 1"}
            else:
                collection.update_one(
                {"id": data.id},
                {"$push":{"Books": {"book": data.book, "status": 1 , "state": 0, "image": f"{Domain}/get_image/{data.book}" ,"idx": data.idx , "onread": False, "Done": False }}}
                )
                return{"detail": "Added but status 2 "} 
        else:
            collection.insert_one({"id": data.id, "name": data.name,"Books": [{"book": data.book, "status": 1, "state": 0 ,"image": f"{Domain}/get_image/{data.book}" ,"idx": data.idx , "onread": False, "Done": False }]})
            return{"detail": "Addedx"}  
       
    elif existing_data:
        existing_datas = list(collection.find({"Books.book": data.book, "id": data.id,"Books.status": 2 }))   
        if existing_datas:
            collection.update_one(
            {"id": data.id, "Books.book": data.book},
            {"$set": {"Books.$.status": 1,  }}
            )
            return{"detail": "Added"} 
        else:
            return{ "detail":"has added already"}
    
@app.post("/mark_as_onread/")
async def read_root(data: Onread):
    id = data.id
    book = data.book
    collection = db.get_collection("Addbook")
    existing_data = list(collection.find({"Books.book": book,"id": id}))
    for item in existing_data:
        item["_id"] = str(item["_id"])  
    if existing_data == []:
        existing_books = list(collection.find({ "id": id}))
        for item in existing_books:
            item["_id"] = str(item["_id"])  
            
        if existing_books:
            collection.update_one(
                {"id": id},
                {"$push":{"Books":{"book": data.book, "image": data.image , "status": 2, "state": 1 ,"inread": data.inread, "image": f"{Domain}/get_image/{data.book}" , "idx": data.idx , "onread": True, "Done": False }}}
            )
            return {"detail": "existed"}
        else:
            collection.insert_one({"id": id, "name": data.name,"Books": [{"book": data.book, "image": data.image , "status": 2, "inread": data.inread , "state": 1 ,"image": f"{Domain}/get_image/{data.book}",  "idx": data.idx , "onread": True, "Done": False }]})
            return{"detail": "Added"}   
    if existing_data:
        collection.update_one(
            {"id": id, "Books.book": book},
            {"$set": {"Books.$.onread": True, "Books.$.inread": data.inread, "Books.$.state": 1 }}
        )
        return {"detail": "added onread true"}
    

    
@app.post("/Onrating")
async def read_root(data: Onrating):
    collection2 = db.get_collection("Writer")
    collection1 = db.get_collection("Addbook")
    collection3 = db.get_collection("Ebooks")
    existing_data1 = collection1.find_one({"id": data.reader,"Books.book": data.book, "Books.state": 1})
    if existing_data1:
        return{"detail": "Already Added"}
    else:
        existing_data2 = list(collection2.find({"username": data.username,"id": data.id}))
        for item in existing_data2:
            item["_id"] = str(item["_id"])  
        
        if existing_data2 == []:
            return {"detail": "null"}
        else:
            documents = []    
            bookshelf = existing_data2[0].get("YourBook", [])
            for book in bookshelf:
                if "bookshelf" in book and book["bookshelf"] == data.book:
                    documents.append(book)
            if documents: 
                collection2.update_one(
                {"id": data.id, "YourBook.bookshelf": data.book},
                {"$set":{"YourBook.$.reader": documents[0].get("reader") + 1 }}
                )
                collection3.update_one(
                {"id": str(data.id), "filename": data.book},
                {"$set":{"reader": documents[0].get("reader") + 1  }}
                )
                return {"detail": "Success"}
            else:
                return{"detail": "Null"}   
            
# @app.post("/rate")
# async def read_root(data: rates):
#     collection1 = db.get_collection("rating")
#     existing_data1 = collection1.find_one({"id": data.id,"Books.book": data.book})
#     existing_data2 = collection1.find_one({"id": data.id,"Books.book": data.book})
#     if existing_data1:
#         # rated = collection1.find_one({"rating": data.rating})
#         # if rated:
#         #         return{"detail": "Already rated"} 
#         # else:
#         #     collection1.update_one({"id": data.id,"Books.book": data.book} ,{"$set": {"rating": data.rating}}) 
            
#         return{"detail": "Already Added"}
#     elif existing_data2:
#         return {"detail": "rating"}
#     else:
#         return{"detail": "read"}
#         # collection1.insert_one(dict(data)) 

@app.post("/Delete")
async def read_root(data: rates):
    collection1 = db.get_collection("Writer")
    collection2 = db.get_collection("Ebooks")
    existing_data2 = collection1.find_one({"id": data.id,"username": data.name})

    if existing_data2:
        # collection1.delete_many(dict(data)) 
        collection1.delete_one({"YourBook.bookshelf": data.book})
        return{"detail":[{"id": data.id, "name": data.name}]}
    else:
        return{"detail": "No data"}     
    
@app.post("/remove_book/")
async def read_root(data: Removebook):
    collection = db.get_collection("Addbook")
    existing_user = collection.find_one({"id": data.id})
    if existing_user is None:
        raise JSONResponse(status_code=404, detail="User not found")
    
    elif existing_user:
        existing_datas = list(collection.find({"Books.book": data.book, "id": data.id,"Books.status": 1 }))   
        if existing_datas:
            collection.update_one(
            {"id": data.id, "Books.book": data.book},
            {"$set": {"Books.$.status": 2  }}
            )
            return{"detail": "Added"} 
    return{"detail" : "Removed"}

@app.post("/mark_as_done/")
async def read_root(data: Process):
    id = data.id
    book = data.book
    collection = db.get_collection("Addbook")
    # existing_data = collection.find_one({"Books.book": book})
    existing_book = list(collection.find({"Books.book": data.book, "id": data.id}))   
    for item in existing_book:
        item["_id"] = str(item["_id"])  
        
    if existing_book:
        collection.update_one(
            {"id": id, "Books.book": book},
            {"$set": {"Books.$.Done": True, "Books.$.inread": 0 , "Books.$.onread": False}}
        )
        return {"detail": "Done"}
    
@app.post('/writer')
async def writer(data: Writers):
    collection = db['Writer']
    data1 = collection.find_one({"username": data.username})
    
    if data1:
        return {"detail": "Already has account"}
    else:
        collection.insert_one(data.dict())
    
        return{"detail": "Congratulation"}    
    
@app.post('/author')
async def author(data: Author):
    collection = db['Writer']
    data1 = list(collection.find({"username": data.username}))
    
    for item in data1:
        item["_id"] = str(item["_id"])  
    
    if data1 != []:
        return data1[0]
    else:
        return {"detail": "not existed"}     
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=Port)
    

# a = 10
# b = 11

# if (a > b):
#     print('log1')
# else :
#     print('log2')
# def greet(name):
#     return f"Hello, {name}!"

# if __name__ == "__main__":
    # name = sys.argv[1]
    # greeting = greet(name)
# print('Hello Worla')