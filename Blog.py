import pymongo
from Config import Configurations
import requests
import random
import string
from datetime import datetime
from UserAPI import DataAPI

class Blog(DataAPI):
    def __init__(self):
        self.config=Configurations()
        self.storage=self.config.Setup_Storage()
        self.mongo_conn=self.config.create_mong_conn()
    
    def generate_post_id(self,length=6):
   
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for _ in range(length))
        return random_string
        
    def create_new_post(self,data):
        post_id=self.generate_post_id(6)
        blog_pic_url=None
        
        db=self.mongo_conn['Blogs']
        collection=db['allBlogPost']
        
        user_blog=db[data['email']]
        if(data['bimgs']):
            self.save_profile(data['bimgs'],post_id)
            blog_pic_url=self.get_profile_pic(post_id)
        else:
            print(data['bimgs'])
            print("*"*100)
        
        data={
            'post_id':post_id,
            'email':data['email'],
            'username':data['username'],
            'title':data['title'],
            'description':data['description'],
            'blog_pic':blog_pic_url,
            'content':data['content'],
            'profile_pic':self.get_profile_pic(data['username']),
            'date':datetime.now().strftime("%b %d, %Y")
            
            
        }
        try:
            collection.insert_one(data)
            user_blog.insert_one(data)
            return True
        except:
            return False
        
    def get_all_blog_posts(self):
        db=self.mongo_conn['Blogs']
        collection=db['allBlogPost']
        
        cursor=collection.find({})
        
        blogs={}
        
        blogs['_id']=list()
        
        for doc in cursor:
            for key,value in doc.items():
                if key not in blogs:
                    blogs[key]=list()
                blogs[key].append(value)
                
        return blogs
    
    def get_specific_blog(self,blog_id):
        collection=self.mongo_conn['Blogs']['allBlogPost']
        
        cursor=collection.find({"post_id":blog_id})
        
        specific_blog={}
        
        
        for doc in cursor:
            for key,value in doc.items():
                specific_blog[key]=value
        return specific_blog
                
                
        
        
        