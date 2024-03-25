from fastapi import  FastAPI, File, UploadFile, Form, HTTPException, Body, Cookie,Header
from pymongo import MongoClient
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pathlib import Path
from pydantic import ValidationError
import os
import io
import random
import base64
from fastapi.middleware.cors import CORSMiddleware
import jwt
from bson import ObjectId
from typing import Optional, Dict, Any

Port = 8000
Domain = 'http://localhost:8000'
SECRET_KEY = "748"

def create_token(data: dict, secret:str, expires_delta: int):
    to_encode = data.copy()
    print(secret,"here")
    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str, secret:str):
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"key": "Token has expired"}
    except jwt.DecodeError:
        return {"key": "Invalid"}

user_data = "true"
# token = create_token({"key": user_data}, SECRET_KEY, expires_delta=3600)  
# decoded_token = decode_token(token, SECRET_KEY)
# print(decoded_token,token, 'ss')

def print_and_increment():
    if not hasattr(print_and_increment, 'counter'):
        print_and_increment.counter = 1
    else:
        print_and_increment.counter += 1

    return print_and_increment.counter

# print_and_increment() 


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost:3000",  
    "https://ebookz.store/"
]

client = MongoClient("mongodb+srv://Joben:Anne060123@joben.a1aoz0g.mongodb.net/?retryWrites=true&w=majority")
db = client["Users"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    Unique: str
class DeleteFileInput(BaseModel):
    file_name: str  
    Book: str  
    Unique: str
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
    name: str
    idx: int

class AddFavorite(BaseModel):
    id: int
    book: str
    name: str
    
class AddPageNumber(BaseModel):
    id: int
    book: str
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
    id: str

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
    id: str
    
    
    
        #   --------------------------- Ebooks -----------------------------------   #
    
@app.get("/get_data/")
async def get_data( ):
    collection = db["Ebooks"]
    data = list(collection.find({}))
    
    if data == []: 
        return {"detail":"Empty"}
    for item in data:
        item["_id"] = str(item["_id"])
        item.pop("content", None)

    return JSONResponse(content=data)
    
    
        #   --------------------------- Register Account -----------------------------------   #
    
@app.post("/register")
async def create_item(data: Register):
    name = data.name
    password = data.password  
    collection = db.get_collection("Users")
    data2 = list(collection.find({}))
    data3 = list(collection.find({ "name": name, "password": password}))
    for item in data3:
        item["_id"] = str(item["_id"]) 
    if(name == "" or password == "" ):
        error_message = "null"
        return JSONResponse(content={"message": error_message}, status_code=200)
    
    elif data3:
        return JSONResponse(content={"message": "null"}, status_code=200)
    
    elif not data3 :
        random_Number = str(random.randint(1,1000))
        length = len(data2)
        create_id =  data2[length - 1].get("id") + 1 if length >= 1 else 0
        token = create_token({"key": name}, random_Number, expires_delta=3600)  
        user_Data = {"name": name , "password": password , "id": create_id , "token" : token, "Key": random_Number, "Writer": 0}
        user_response = {key: value for key, value in user_Data.items() if key != "Key" and key != "password" }
        collection.insert_one(user_Data) 
        # response = JSONResponse(content=user_response, status_code=200)
        # response.set_cookie(key="my_token", value=random_Number, max_age=3600, httponly=True, secure=True, samesite="Strict")
        return user_response
    
    
    
        #   --------------------------- Login Account -----------------------------------   #
        
  
@app.post("/login")
async def create_item( data: Login,  my_token: str = Cookie(None), ticket: str = Header(None)):
    collection = db["Users"]
    password = data.password
    name = data.name
    data2 = list(collection.find({"name": name, "password": password}))
    for item in data2:
        item["_id"] = str(item["_id"])  
    if not data2 :
        return JSONResponse(status_code=200,content={"detail": "Not existed"})
    else:
        random_Number = str(random.randint(1,1000))
        token = create_token({"key": name}, random_Number, expires_delta=3600)
        collection.update_one({"name": name},
        {"$set":{"token": token, "Key": random_Number }})
        data3 = list(collection.find({"name": name, "password": password}))
        for item in data3:
            item["_id"] = str(item["_id"])  
        user_Data = data3[0]
        user_response = {key: value for key, value in user_Data.items() if key != "Key" and key != "password" }
        # response = JSONResponse(content=user_response, status_code=200)
        return user_response
    
    
        #   --------------------------- User Account -----------------------------------   #
    
@app.post("/AccountInfo/")
async def get_data(token: str = Header(None), id: str = Header(None)):
    collection = db["Users"]
    if id and token :
        data2 = list(collection.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket["key"] != "Invalid":
            user_response = {key: value for key, value in data2[0].items() if key != "Key" and key != "password" and key != "token" }
            return user_response
        else:
            raise HTTPException(status_code=404 )
    else:
        raise HTTPException(status_code=404) 
    
    
        #   --------------------------- Writer -----------------------------------   #
    
@app.post('/writer')
async def writer(data: Writers, token: str = Header(None), id: str = Header(None)):
    collection = db['Users']
    if id and token :
        data2 = list(collection.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket and data2:
            collection.update_one(
                {"id": int(id)},
                {"$set": {"Writer": 1}}
            )
            return{"detail": data2}
        else:
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id","data": False}
    
    
        #   --------------------------- Upload Book -----------------------------------   #

@app.post("/UploadFile/")
async def create_upload_file( filename: str = Form(...), Author1: str = Form(...), Id: str = Form(...), Unique: str = Form(...) , token: str = Header(None), id: str = Header(None)):
    collection_book = db.get_collection("Ebooks")
    collection_user = db['Users']
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
            collection_book.insert_one({"filename": filename, "image": f"{Domain}/get_image/{filename}", "id": Id , "_id": Unique , "author": Author1, "reader": 0 , "rating": 0  })
            return {"detail": "Added Book"}
        else:
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id","data": False}
    

#   --------------------------- create_text_file -----------------------------------   #

@app.post("/create_text_file/")
async def create_text_file(text_data: TextFileInput,  token: str = Header(None), id: str = Header(None)):
    collection_user = db['Users']
    collection = db.get_collection("Ebooks")
    file_name = text_data.file_name
    text_content = text_data.text_content
    Book_store = text_data.Book
    existing_user = collection.find_one({"_id": text_data.Unique})
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
            if existing_user:       
                chapters = existing_user.get("Chapter", [])
                for chapter in chapters:
                    title = chapter.get("Title")
                    if title:
                        collection.update_one(
                            {"filename": Book_store, "Chapter.Title": file_name },
                            {"$set": {"Chapter.$.Title": file_name , "Chapter.$.content": text_content  }}
                        )            
                        return{"status": "Edited"}
                    else:
                        collection.update_one(
                            {"filename": Book_store, "_id": text_data.Unique },
                            {"$push":{"Chapter": {"Title": file_name, "content" : text_content }}}
                        )            
                        return{"status": "Added"}
            else:
                return { "status": False, "Message": "Wrong Data"}
        else:
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id","data": False}
    
    
    
   #   --------------------------- create_text_file -----------------------------------   #

@app.post("/delete_file/")
async def create_text_file(text_data: DeleteFileInput,  token: str = Header(None), id: str = Header(None)):
    collection = db.get_collection("Ebooks")
    file_name = text_data.file_name
    Book_store = text_data.Book
    existing_user = collection.find_one({"_id": text_data.Unique})
    collection_user = db['Users']
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
            if existing_user:       
                chapters = existing_user.get("Chapter", [])
                for chapter in chapters:
                    title = chapter.get("Title")
                    if title:
                        collection.update_one(
                            {"filename": Book_store, "Chapter.Title": file_name },
                              {"$pull": {"Chapter": {"Title": file_name}}},
                        )            
                        return{"status": "Deleted", "data": True}
                    else:           
                        return{"status": "Chapter not existed" , "data": False}
            else:
                return { "status": False, "Message": "Wrong Data"}
        else:
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id","data": False} 
    
    
     #   --------------------------- get_user_data -----------------------------------   #   


    
@app.get("/get_user_data/")
async def get_data():
    collection = db["Users"]
    data = list(collection.find({}))
    data1 = len(data)
    data2 = 111 if data1 > 1 else 0
    for item in data:
        item["_id"] = str(item["_id"]) 
    return {"data": data, "length": data1}


     #   --------------------------- Add To Read -----------------------------------   #   


@app.post("/add_book/")
async def read_root(data: Addbook, token: str = Header(None), id: str = Header(None)):
    collection = db.get_collection("Readers")
    existing_user = list(collection.find({"id": data.id}))
    for item in existing_user:
        item["_id"] = str(item["_id"]) 
    collection_user = db['Users']
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
            if existing_user == []:
                collection.insert_one({"id": data.id, "name": data.name,"Books": [{"book": data.book , "page" : data.idx , "favorite": False , "reading" : True}]})
                return{"detail": "Added"}  
            else:
                collection.update_one(
                        {"id": data.id, "Books.book": data.book},
                        {"$push":{"Books": {"book": data.book , "page" : 0 , "favorite": False, "reading" : True }}}
                )    
                return{"detail": "Read"}  
        else:
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id","data": False} 
    
    #   --------------------------- Add To Favorite -----------------------------------   #   
    
    
@app.post("/add_favorite/")
async def read_root(data: AddFavorite,  token: str = Header(None), id: str = Header(None)):
    collection =db['Readers']
    existing_user = list(collection.find({"id": data.id}))
    for item in existing_user:
        item["_id"] = str(item["_id"]) 
    collection_user = db['Users']
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
            if existing_user == []:
                collection.insert_one({"id": data.id, "name": data.name,"Books": [{"book": data.book , "page" : 0 , "favorite": True , "reading" : True}]})
                return{"detail": False}  
            else:
                collection.update_one(
                        {"id": data.id, "Books.book": data.book},
                        {"$set":{"Books.$.favorite": True }}
                )    
                return{"detail": True}  
        else:
            
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id","data": False} 
    
      
        
        
        #   --------------------------- Page Number -----------------------------------   #   
    
    
@app.post("/add_pageNumber/")
async def read_root(data: AddPageNumber,token: str = Header(None), id: str = Header(None)):
    collection = db['Readers']
    existing_user = list(collection.find({"id": data.id}))
    for item in existing_user:
        item["_id"] = str(item["_id"])  
    collection_user = db['Users']
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
            if existing_user == []:
                return{"detail": False}  
            else:
                collection.update_one(
                        {"id": data.id, "Books.book": data.book},
                        {"$set":{"Books.$.page": data.idx }}
                )    
                return{"detail": True}  
        else:
            
            raise HTTPException(status_code=404 )
    else:
        return {"detail": "No token and Id", "data": False} 
    

        #   --------------------------- Added Books -----------------------------------   #  
        
        
        
@app.post("/Added_books/")
async def get_data(data: Optional[Dict[str, Any]] = Body(None),token: str = Header(None), id: str = Header(None)):
    collection = db['Readers']
    collection_user = db['Users']
    iD = data.get("id")
    if id and token :
        data2 = list(collection_user.find({"id": int(id) }))
        for item in data2:
            item["_id"] = str(item["_id"]) 
        decode_Ticket = decode_token(str(token), data2[0]["Key"])
        if decode_Ticket:
    
            if not iD:
                return {"data": "Empty"}
            else:
                data3 = list(collection.find({"id": int(iD)}))
                for item in data3:
                    item["_id"] = str(item["_id"])  
                    
                return data3
    else:
        return {"detail": "No token and Id", "data": False} 


        #   --------------------------- Image Books -----------------------------------   #  

@app.get("/get_image/{file_id}")
async def get_image(file_id: str):
    collection = db.get_collection("Ebooks")
    result = collection.find_one({"filename": file_id})
    if result:
        content = result.get("content")
        return StreamingResponse(io.BytesIO(content), media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Image not found")

        #   --------------------------- Readers -----------------------------------   #  
      
@app.post("/Readers")
async def read_root(data: Onrating):
    # collection2 = db.get_collection("Writer")
    collection_read = db.get_collection("Readers")
    collection3 = db.get_collection("Ebooks")
    existing_data1 = collection3.find_one({"_id": data.reader,"filename": data.book})
    if existing_data1:
                collection3.update_one(
                {"id": data.id, "filename": data.book},
                {"$set":{"reader":  1 }}

                )
    #     return{"detail": "Already Added"}
    # else:
        # existing_data2 = list(collection2.find({"username": data.username,"id": data.id}))
        # for item in existing_data2:
        #     item["_id"] = str(item["_id"])  
        
        # if existing_data2 == []:
        #     return {"detail": "null"}
        # else:
        #     documents = []    
        #     bookshelf = existing_data2[0].get("YourBook", [])
        #     for book in bookshelf:
        #         if "bookshelf" in book and book["bookshelf"] == data.book:
        #             documents.append(book)
        #     if documents: 
        #         collection2.update_one(
        #         {"id": data.id, "YourBook.bookshelf": data.book},
        #         {"$set":{"YourBook.$.reader": documents[0].get("reader") + 1 }}
        #         )
        #         collection3.update_one(
        #         {"id": str(data.id), "filename": data.book},
        #         {"$set":{"reader": documents[0].get("reader") + 1  }}
        #         )
        #         return {"detail": "Success"}
        #     else:
        #         return{"detail": "Null"}  
            
            


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


# @app.post('/YourBook')
# async def writer(data: Stories):
#     collection = db['Users']
#     data1 = collection.find_one({"id": data.id})
    
#     if data1:
#         collection.update_one(
#             {"id": data.id},
#             {"$push": {"YourBook":{"bookshelf": data.book, "reader": 0, "rating": 0}}})
#     else:    
#         return{"detail": "Nodata"}  


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
    
    
# @app.post("/mark_as_onread/")
# async def read_root(data: Onread):
#     id = data.id
#     book = data.book
#     collection = db.get_collection("Readers")
#     existing_data = list(collection.find({"Books.book": book,"id": id}))
#     for item in existing_data:
#         item["_id"] = str(item["_id"])  
#     if existing_data == []:
#         existing_books = list(collection.find({ "id": id}))
#         for item in existing_books:
#             item["_id"] = str(item["_id"])  
            
#         if existing_books:
#             collection.update_one(
#                 {"id": id},
#                 {"$push":{"Books":{"book": data.book, "image": data.image , "status": 2, "state": 1 ,"inread": data.inread, "image": f"{Domain}/get_image/{data.book}" , "idx": data.idx , "onread": True, "Done": False }}}
#             )
#             return {"detail": "existed"}
#         else:
#             collection.insert_one({"id": id, "name": data.name,"Books": [{"book": data.book, "image": data.image , "status": 2, "inread": data.inread , "state": 1 ,"image": f"{Domain}/get_image/{data.book}",  "idx": data.idx , "onread": True, "Done": False }]})
#             return{"detail": "Added"}   
#     if existing_data:
#         collection.update_one(
#             {"id": id, "Books.book": book},
#             {"$set": {"Books.$.onread": True, "Books.$.inread": data.inread, "Books.$.state": 1 }}
#         )
#         return {"detail": "added onread true"}


    
    
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
