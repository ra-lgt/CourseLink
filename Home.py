from flask import Flask,render_template,request,jsonify,session,url_for,redirect
import json
import random
from Config import Configurations
from mail import send_email
from datetime import datetime


app=Flask(__name__)
config=Configurations()
firebase_db=config.Setup_auth()
app.secret_key = 'Course-Link'
mail=send_email()
mongo_client=config.create_mong_conn()


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

@app.route('/sucess_register')
def sucess_register():
    return render_template('success.html',data="THANKS FOR REGISTERING")

@app.route('/login',methods=['POST','GET'])
def login():
    if(request.method=='POST'):
        email=request.form['loginemail']
        password=request.form['loginPassword']
    
    try:
        userauth=firebase_db.sign_in_with_email_and_password(email,password)
    except:
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
            'Level_preparation':"Not Set",
            'language':"Not Set",
            'Joined_date':current_date.strftime("%Y-%m-%d")
            })
    
    firebase_db.create_user_with_email_and_password(data['email'],data['password'])
    


    session['username']=''
    session['email']=''
    session['phone']=''
    session['password']=''


    response_data = {'message': 'Signup successful'}

    return jsonify(response_data), 200 


@app.route('/send_otp',methods=['GET','POST'])
def send_otp():
    response_data = {'message': 'Signup successful','email_exists':False}
    print("helloo world")

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

    



@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/terms')
def terms():
    return "hello"

@app.route('/blog')
def blog():
    return render_template('blog.html')
    

if __name__=="__main__":
    app.run(debug=True)