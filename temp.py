from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import base64

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('temp_1.html')

@socketio.on('image')
def handle_image(data):
    # Decode base64 image data
    image_data = base64.b64decode(data['image'])
    
    # Save the image to a file or process it as needed
    with open('received_image.png', 'wb') as f:
        f.write(image_data)
    
    # You can also emit a response back to the client if needed
    emit('response', {'message': 'Image received successfully'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
