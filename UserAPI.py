import pymongo
from Config import Configurations
import requests



class DataAPI:
    def __init__(self):
        self.config=Configurations()
        self.mongo_conn=self.config.create_mong_conn()
        
    def get_all_user_data(self,email):
        db = self.mongo_conn["User-Data"]
        collection=db['user_details']
        
        
#         query = {
#     "$and": [
#         {"email": {"$ne": email}},
        
#     ]
# }
        
        cursor = collection.find({})
        
        user_all_data={}
        
        #have to check whether the user is already a friend or not
        # user_all_data['profile_url']=list()
        
        for doc in cursor:
            for key,value in doc.items():
                
                if key not in user_all_data:
                    user_all_data[key]=list()
                user_all_data[key].append(value)
                
                # if(key=="username"):
                    
                #     user_all_data['profile_url'].append(self.get_profile_pic(value))
                    
                    
        try:        
            del user_all_data['_id']
        except:
            pass
        
        return user_all_data
    
    def get_data_of_specific_user(self,email):
        db = self.mongo_conn["User-Data"]
        collection=db['user_details']
        
        cursor = collection.find({"email":email})
        
        data=None
        for doc in cursor:
            data=doc
            break
        
        return data