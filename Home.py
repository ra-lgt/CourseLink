

from flask import Flask,render_template,request,jsonify,session,url_for,redirect
import json
import random
from Config import Configurations
from mail import send_email
from datetime import datetime
from flask_caching import Cache
from UserAPI import DataAPI
from chat import Chat
from flask_socketio import SocketIO, emit,join_room,leave_room,send
from flask_cors import CORS
import threading
from Blog import Blog

app = Flask(__name__)
socketio = SocketIO(app)

config=Configurations()
firebase_db=config.Setup_auth()
app.secret_key = 'Course-Link'
mail=send_email()
mongo_client=config.create_mong_conn()
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
user_dataAPI=DataAPI()
user_chat=Chat()
CORS(app)
user_blog=Blog()

#helping functions
def generate_otp():
    sequence_length = 5
    min_value = 10 ** (sequence_length - 1)  # Smallest 5-digit number (10000)
    max_value = (10 ** sequence_length) - 1  # Largest 5-digit number (99999)
    random_number = random.randint(min_value, max_value)
    return random_number

def check_email_exists(email):
    try:
        users = firebase_db.get_user_by_email(email)
        return True
    except Exception as e:
        return False
    
#end of helping functions

@app.route('/')
def Home():
    session_bool=False
    
    if('user_id' in session):
        session_bool=True
    
    
    return render_template('index.html',session_bool=session_bool)

@app.route('/signup_login')
def signup_login():
    return render_template('signup_login.html')



@app.route('/success')
def success():
    data=request.args.get('data')
    return render_template('success.html',data=data)



@app.route('/login',methods=['POST','GET'])
def login():
    if(request.method=='POST'):
        email=request.form['loginemail']
        password=request.form['loginPassword']
    
    try:
        userauth=firebase_db.sign_in_with_email_and_password(email,password)
        session['email']=email
        session['username']=user_dataAPI.get_data_of_specific_user(email)['username']
  
    except Exception as e:
        print(e)
        error_url = url_for('error', data="Invalid login", reason="Check your credentials and try again or contact us")
        return redirect(error_url)
    
    cookie=userauth['idToken']
    session['user_id'] = cookie
    return redirect(url_for('Home'))

@app.route('/signup',methods=['GET','POST'])
def signup():

    
    database=config.Setup_DataBase()


    data={
        'username':session.get('username'),
        'email':session.get('email'),
        'phone':session.get('phone'),
        'password':session.get('password'),
        
        
        }

    db=mongo_client['User-Data']
    collection=db['user_details']
    current_date = datetime.now()
    
    existing_document = collection.find({'email': data['email']})
    
    if existing_document is not None:
            response_data = {'message': 'Signup successful'}

            return jsonify(response_data), 200 

    collection.insert_one({
            'username':data['username'],
            'email':data['email'],
            'phone':data['phone'],
            'password':data['password'],
            'Age':"Not Set",
            'Course':"Not Set",
            'About':"Not Set",
            'first_name':"Not Set",
            'last_name':"Not Set",
            'City':"Not Set",
            'Country':"Not Set",
            'Degree':"Not Set",
            'Experince_Level':"Not Set",
            'language':"Not Set",
            'postal_code':"Not Set",
            'Joined_date':current_date.strftime("%Y-%m-%d")
            })
    
    firebase_db.create_user_with_email_and_password(data['email'],data['password'])
    


    session['username']=''
    session['email']=''
    session['phone']=''
    session['password']=''


    response_data = {'message': 'Signup successful'}

    return jsonify(response_data), 200 

# @app.route('/profile')
# def profile():
#     return render_template('Profile.html')

@app.route('/send_otp',methods=['GET','POST'])
def send_otp():
    response_data = {'message': 'Signup successful','email_exists':False}


    data=request.get_json()
    flag=check_email_exists(data['email'])

    if(flag==True):
        response_data['email_exists']=True
        return jsonify(response_data),404

    session['username']=data['username'].strip()
    session['email']=data['email'].strip()
    session['phone']=data['phone']
    

    if(data['password']==data['confirm_password']):

        session['password']=data['password']
        get_otp=generate_otp()
        response_data['otp']=str(get_otp)

        mail.send_otp(session['username'],session['email'],get_otp)

        return jsonify(response_data), 200

    response_data['message']='FAIL'

    return jsonify(response_data),404


@app.route('/error')
def error():
    data = request.args.get('data')
    reason = request.args.get('reason')
    return render_template('error.html',data={"data":data,"reason":reason})

@app.route('/email_exists')
def email_exists():
    return render_template('error.html',data={"reason":"Email Already Exists","data":"Try to login using valid credentials"})

    
@app.route('/profile',methods=['GET','POST'])
def profile():
    user_specific_data=None
    user_specific_data=cache.get('profile_data')
    
    # user_specific_event=None
    # user_specific_event=cache.get('event_data')
    
    # friend_data=None
    # friend_data=cache.get('user_friend_data')
    
    # if(friend_data is None):
        
    #     friend_data=friend.get_friends_specific_user(session['email'])
    #     cache.set("user_friend_data",friend_data,timeout=180*60)
    
    
    # if(user_specific_event is None):
    #     user_specific_event=event.get_event_for_user(session['email'])
    #     cache.set('event_data',user_specific_event,timeout=180*60)
    
    if(user_specific_data is None):
        user_specific_data=user_dataAPI.get_data_of_specific_user(session['email'])
        cache.set('profile_data',user_specific_data,timeout=180*60)
    else:
        print("cache Hit")


    # return render_template("profile.html",user_specific_data=user_specific_data,event_count=len(user_specific_event['_id']),friend_count=len(friend_data['_id']))
    return render_template('Profile.html',user_specific_data=user_specific_data)
@app.route('/save_profile_pic',methods=['POST'])
def save_profile_pic():
    
    if 'file' not in request.files:
        print("file not found")
    file = request.files['file']

    return_code=user_dataAPI.save_profile(file,cache.get('profile_data')['username'])
    
    if(return_code==True):
        result = {'message': 'Image uploaded successfully'}
        return jsonify(result)
    else:
        result = {'error': 'Unexpected error occured'}
        return jsonify(result)
    
@app.route('/create_chat',methods=['POST','GET'])
def create_chat():
    data=request.get_json()
    
    return_code=user_chat.start_chat(session['email'],data['email'])    
    
    if(return_code==True):
        return jsonify({'message':"Sucess",'status':200}),200
    
    return jsonify({'message':"Error",'status':404}),404

@app.route('/chat_page/<chat_id>')
def chat_page(chat_id):
    
    user_specific_chats=None
    user_specific_chats=cache.get('users_chats')
    history_chat={}
    len_chat=0
    
    user_specific_data=[]
    
    if(user_specific_chats is None):
        user_specific_chats=user_chat.get_users_chat(session['email'])
        cache.set('users_chat',user_specific_chats,timeout=180*60)
    
    for email in user_specific_chats['chat_reciever_email']:
        data=user_dataAPI.get_data_of_specific_user(email)
        user_specific_data.append(data)
    
    selected_chat={}
    
    if(chat_id!='None'):
        index=user_specific_chats['chat_id'].index(chat_id)
        selected_chat=user_specific_data[index]
        selected_chat['chat_id']=user_specific_chats['chat_id'][index]
        
        history_chat=user_chat.get_specific_chat(chat_id,session['email'])
        len_chat=len(history_chat['_id'])
        
    
    print(selected_chat)    
    print("-"*10)
    print(user_specific_chats)
    print("-"*10)
    print(user_specific_data)
    print("-"*10)
    
        
    return render_template('chat.html',user_specific_data=user_specific_data,user_specific_chats=user_specific_chats,count=len(user_specific_data),chat_id=chat_id,selected_chat=selected_chat,email=session['email'],history_chat=history_chat,len_chat=len_chat,username=session['username'])

@app.route('/change_chat/<chat_id>')
def change_chat(chat_id):
    # specific_chat=user_chat.get_specific_chat(chat_id,session['email'])
    return "hi"
    
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    session['chat_id'] = room
    print(room)
    
@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    
    session.pop('chat_id', None)




@socketio.on('message')
def handle_message(message):
    # Run the background thread
    
    
    
    return_code = user_chat.push_data_specific_chat(message['sender_email'], message['receiver_email'], str(session['username']+':'+message['message']), message['room'])
    print(message['sender_email'])
    print("-" * 30)
    print(message['receiver_email'])
    
    if return_code:
        current_time = datetime.now().time()
        hours, minutes = current_time.hour, current_time.minute
        formatted_time = "{:02d}:{:02d}".format(hours, minutes)

        # Emitting from within a socket event handler
        emit('response', {
            'data': str(session['username']+':'+message['message']),
            'sender_email': message['sender_email'],
            'receiver_email': message['receiver_email'],
            'email':session['email'],
            'time': formatted_time
        }, broadcast=True, room=message['room'])

@app.route('/terms')
def terms():
    return "hello"

@app.route('/create_blog')
def create_blog():
    user_specific_data=None
    user_specific_data=cache.get('profile_data')
    
    if(user_specific_data is None):
        user_specific_data=user_dataAPI.get_data_of_specific_user(session['email'])
        cache.set('profile_data',user_specific_data,timeout=180*60)
        
    return render_template('create_blog.html',username=session['username'],profile_pic=user_specific_data['profile_pic'],date=datetime.now().strftime("%b %d"))

@app.route('/blog/<int:page_no>')
def blog(page_no):
    blog_posts=user_blog.get_all_blog_posts()
    
    
    start=(page_no-1)*1
    
    end=(page_no)*1
    
    if(start>len(blog_posts['_id'])):
        start=(page_no-1)*1
    
    if(end>len(blog_posts['_id'])):
        end=len(blog_posts['_id'])

    return render_template('blog.html',blog_posts=blog_posts,end=end,start=start,page_no_len=len(blog_posts['_id'])//1,page_no=page_no)

@app.route('/post_blog',methods=['POST','GET'])
def post_blog():
    bimgs=None
    if(request.method=='POST'):
        title=request.form['title']
        description=request.form['dscription']
        if 'bimgs'  in request.files:
            bimgs=request.files['bimgs']
        content=request.form['content']
        
        return_code=user_blog.create_new_post(
            {'title':title,
             'description':description,
             'bimgs':bimgs,
             'content':content,
             'email':session['email'],
             'username':session['username']
             }
        )
        if(return_code==True):
            return redirect(url_for('success',data="Successfully Posted"))
        else:
            return redirect(url_for('error',data="Couldn't Upload",reason="Check with admin"))
        
    
@app.route('/find_friends')
def find_friends():
    all_user_data=None
    all_user_data = cache.get('cached_all_user_data')
    
    
    if(all_user_data is None):
        
        all_user_data=user_dataAPI.get_all_user_data(session['email'])
        
        cache.set('cached_all_user_data', all_user_data, timeout=180 * 60)
    else:
        print("Cache hit")
    
    Course=[]
    degree=[]
  
        
    for i,j in zip(all_user_data['Course'],all_user_data['Degree']):
        if(i not in Course and i!="Not Set"):
            Course.append(i)
        if( j not in degree and j!="Not Set"):
            degree.append(j)
    
    if not all_user_data:
        count=0
    else:
        count=len(all_user_data['username'])
    print(all_user_data)
    print("-"*10)
    return render_template('find_friends.html',all_user_data=all_user_data,count=count,Course=Course,degree=degree)

# @app.route('/send_friend_request')
# def send_friend_request():
#     return "hi"
@app.route('/update_profile_data',methods=['POST'])
def update_profile_data():
  
    
    updated_data={}
    
    
    updated_data['first_name']=request.form['f_name']
    updated_data['last_name']=request.form['l_name']
    updated_data['phone']=request.form['phone']
    updated_data['Age']=request.form['age']
    updated_data['Address']=request.form['address']
    updated_data['City']=request.form['city']
    updated_data['Country']=request.form['country']
    updated_data['Postal_Code']=request.form['postal']
    updated_data['About']=request.form['about']
    updated_data['Course']=request.form['Course']
    updated_data['Degree']=request.form['Degree']
    updated_data['Experince_Level']=request.form['Experince_Level']
    updated_data['language']=request.form['language']

    
    # return_code=True
    return_code=user_dataAPI.update_profile(updated_data,session['email'])
    
    if(return_code==True):
        
        cache.clear()
        return redirect(url_for('profile'))
    
    else:
        return redirect(url_for('error',data="Couldn't Update",reason="Try to update again you should have strong internet"))

@app.route('/logout')
def logout():
    # Clear the user ID from the session
    session.pop('user_id', None)
    session.clear()
    cache.clear()
    return redirect(url_for('Home'))

if __name__ == '__main__':
    socketio.run(app,debug=True)