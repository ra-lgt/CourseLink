from flask import Flask,render_template

app=Flask(__name__)


@app.route('/')
def Home():
    return render_template('index.html')



@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')
    

if __name__=="__main__":
    app.run(debug=True)