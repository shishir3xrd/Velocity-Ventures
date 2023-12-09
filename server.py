import uuid
from bson import ObjectId
from flask import Flask, session, render_template, request, redirect, current_app, jsonify,json, flash
from flask_pymongo import PyMongo
import bcrypt, secrets
from src.controllers.admin import admincontrol
from src.controllers.user import usercontrol
from urllib.parse import quote_plus
from flask_socketio import SocketIO
from flask_mail import Mail,Message
from src.utils import send_verification_email 
app = Flask(__name__)

app.config['MAIL_SERVER'] = 'devzhive.com'
app.config['MAIL_PORT'] = 587  # Use your mail server's port
app.config['MAIL_USE_TLS'] = True  # Set to False if using SSL
app.config['MAIL_USE_SSL'] = False  # Set to True if using SSL
app.config['MAIL_USERNAME'] = 'test@devzhive.com'
app.config['MAIL_PASSWORD'] = 'U-*_!7h?iG%%'
app.config['MAIL_DEFAULT_SENDER'] = 'test@devzhive.com'
mail = Mail(app)

app.config["SECRET_KEY"] = secrets.token_hex(16) 
username = 'shishirsaha830'
password = 'ss1234@'
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

app.config["MONGO_URI"] = f'mongodb+srv://{escaped_username}:{escaped_password}@cluster0.tedb4pk.mongodb.net/velocity_ventures'
mongo = PyMongo(app)

app.register_blueprint(admincontrol,url_prefix="/admin")
app.register_blueprint(usercontrol, url_prefix="/user")


@app.route('/')
def index():
    login_message = session.get('login_message')
    registration_message = session.get('registration_message')
    return render_template("index.html", login_message=login_message, registration_message=registration_message)


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    nid = request.form['nid']
    mobile_number = request.form['mobile_number']
    address = request.form['address']
    gender = request.form['gender']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if the user already exists in the database
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        session['registration_message'] = "User with this email already exists"
        return redirect('/')

    # Check if the passwords match
    if password != confirm_password:
        session['registration_message'] = "Passwords do not match"
        return redirect('/')

    # Hash the password before storing in the database
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert the user data into the database
    user_data = {
        "name": name,
        "email": email,
        "nid": nid,
        "mobile_number": mobile_number,
        "address": address,
        "gender": gender,
        "password": hashed_password,
        "2fa": False
    }
    mongo.db.users.insert_one(user_data)

    session['registration_message'] = "Registration successful"
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Check if the user exists in the database
    user = mongo.db.users.find_one({"email": email}) 
    if not user:
        session['login_message'] = "User not found"
        return redirect('/')
    
    if email == "admin@gmail.com" and password == "admin":
        return redirect('/admin/admin_dashboard')
    
    # Verify the password
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        if user.get("2fa",False)==True:
            token = str(uuid.uuid4()) #unique string 
            mongo.db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"token": token}})
            
            send_verification_email(mail, user, token) 
            session['login_message'] = "2 step verification link has been sent to your email successfully."
        else:
            session['email'] = user['email']  #without two step
            return redirect('/user/')     
    else:
        session['login_message'] = "Incorrect password"
    return redirect('/#loginPopup')

@app.route('/two_step_verification', methods=['GET'])
def two_step_verification():
    token = request.values.get('token') 

    # Check if the user exists in the database
    user = mongo.db.users.find_one({"token": token})
    if (not user) or token == "_":
        session['login_message'] = "Token expired or already used."
        return redirect('/')
    mongo.db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": {"token": "_"}})
    session['email'] = user['email']
    return redirect('/user/') 
    
@app.route('/forget_password')
def forget_password():
    return render_template("forget_password.html")

@app.route('/send_email', methods=['GET', 'POST']) 
def send_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        subject = 'Hello from Flask-Mail'
        body = render_template('email_template.html', name=recipient)

        # Create the email message
        message = Message(subject=subject, recipients=[recipient], html=body)

        try:
            # Send the email
            mail.send(message)
            flash('Email sent successfully!', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')


socketio = SocketIO(app)

@app.route('/chat/System')
def sessions():
    return render_template('chat.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=52010) 