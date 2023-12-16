import pymongo
from Config import Configurations
import requests
import random
import string
from datetime import datetime


class Chat:
    def __init__(self):
        self.config=Configurations()
        self.mongo_conn=self.config.create_mong_conn()
        
    def generate_chat_id(self,length=6):
   
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for _ in range(length))
        return random_string
        
    
    def start_chat(self,sender_email,reciever_email):
        db=self.mongo_conn['ChatDB']
        collection_sender=db[sender_email]
        collection_reciever=db[reciever_email]
        
        chat_id=self.generate_chat_id(length=6)
        
        try:
        
            collection_sender.insert_one({
                'chat_id':chat_id,
                'chat_email_sender':sender_email,
                'chat_reciever_email':reciever_email
            })
            collection_reciever.insert_one({
                'chat_id':chat_id,
                'chat_email_sender':reciever_email,
                'chat_reciever_email':sender_email
            }) 
            return True
        except:
            return False    
    
    def get_users_chat(self,email):
        db=self.mongo_conn['ChatDB']
        collection=db[email]
        
        cursor=collection.find({})
        
        user_chat={}
        
        user_chat['_id']=list()
        
        for doc in cursor:
            for key,value in doc.items():
                if key not in user_chat:
                    user_chat[key]=list()
                user_chat[key].append(value)
        return user_chat
    
    def get_specific_chat(self,chat_id,email):
        db=self.mongo_conn['ChatDB']
        # collection=db[email]
        return "hi"
    
    def push_data_specific_chat(self,sender_email,reciever_email,message,chat_id):
        
        db=self.mongo_conn['all_chats']
        collection=db[chat_id]
        
        data={
            'sender_email':sender_email,
            'reciever_email':reciever_email,
            'chat_id':chat_id,
            'time':datetime.now().strftime("%y%m%d"),
            'message':message
        }
        try:
            collection.insert_one(data)
            return True
        except:
            return False
        
        
        
        
        
                
           
        
        