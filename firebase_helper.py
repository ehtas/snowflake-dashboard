import pyrebase4 as pyrebase

from config import FIREBASE_CONFIG

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])
        email_verified = user_info['users'][0]['emailVerified']
        if not email_verified:
            return None, "Email not verified. Please verify your email first."
        return user, None
    except Exception as e:
        return None, str(e)

def signup_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        return user, None
    except Exception as e:
        return None, str(e)

def logout_user():
    return None
