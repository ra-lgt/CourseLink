import pymongo
from Config import Configurations




class Admin:
    def __init__(self):
        self.config=Configurations()
        self.mongo_conn=self.config.create_mong_conn()
        
    
    def get_all_user_data(self):
        collection=self.mongo_conn['User-Data']['user_details']
        
        user_data={}
        user_data['_id']=list()
        cursor=collection.find({})
        
        for doc in cursor:
            for key,value in doc.items():
                if key not in user_data:
                    user_data[key]=list()
                user_data[key].append(value)
        
        return user_data
        