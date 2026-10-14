import smtplib
from email.message import EmailMessage
import random
import streamlit as st
import hashlib
import database as db

# ==========================================
# 🔐 HASHING UTILITY
# ==========================================
def hash_password(password):
    """
    Encrypts the password using SHA-256 so we don't save raw passwords in the database.
    Built-in library ensures it works flawlessly across Windows/Mac without extra installations.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ==========================================
# 🚪 REGISTRATION
# ==========================================
def register_user(username, email, password, block, sec_q, sec_a):
    """
    Handles new user signup. Validates inputs and hashes passwords.
    """
    # 1. Clean up inputs
    username = username.strip()
    email = email.strip().lower()
    sec_a = sec_a.strip().lower() # Lowercase answer to make it easier to match later
    
    # 2. Basic validation check
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."
    
    # 3. Hash security elements
    hashed_pw = hash_password(password)
    hashed_sec_a = hash_password(sec_a)
    
    # 4. Attempt to create user in database
    success = db.create_user(username, email, hashed_pw, block, sec_q, hashed_sec_a)
    
    if success:
        return True, "Account created successfully!"
    else:
        # Check if the conflict is the username or the email
        existing_user = db.get_user(username)
        if existing_user and existing_user['username'] == username:
            return False, "Username already exists. Please choose another."
        return False, "Email already registered. Please log in."

# ==========================================
# 🔑 LOGIN
# ==========================================
def login_user(identifier, password):
    """
    Verifies user credentials. Accepts either Username OR Email.
    """
    identifier = identifier.strip()
    if "@" in identifier:
        identifier = identifier.lower()
    
    # Check if user exists in database
    user = db.get_user(identifier)
    
    if not user:
        return False, "User not found. Please check your username/email."
        
    # Hash the typed password and compare it to the saved hash
    hashed_pw = hash_password(password)
    if user['password'] == hashed_pw:
        # Successful login! Return True and their formal Username (in case they logged in via email)
        return True, user['username']
    else:
        return False, "Incorrect password."

# ==========================================
# 🔄 PASSWORD RESET LOGIC
# ==========================================
def get_security_question(identifier):
    """
    Step 1 of reset: Finds the user and returns their custom security question.
    """
    identifier = identifier.strip()
    if "@" in identifier:
        identifier = identifier.lower()
        
    user = db.get_user(identifier)
    
    if user:
        return True, user['sec_q']
    else:
        return False, "No account found with that username or email."

def reset_password(identifier, provided_answer, new_password):
    """
    Step 2 of reset: Checks if the security answer is correct, then updates the password.
    """
    identifier = identifier.strip()
    if "@" in identifier:
        identifier = identifier.lower()
        
    provided_answer = provided_answer.strip().lower()
    
    if len(new_password) < 4:
        return False, "New password must be at least 4 characters long."

    user = db.get_user(identifier)
    if not user:
        return False, "Error locating user."
        
    hashed_answer = hash_password(provided_answer)
    
    if user['sec_a'] == hashed_answer:
        # Answer is correct! Update password
        new_hashed_pw = hash_password(new_password)
        db.update_password(identifier, new_hashed_pw)
        return True, "Password successfully reset! You can now log in."
    else:
        return False, "Incorrect answer to the security question."
        # ==========================================
# 📧 EMAIL OTP LOGIC
# ==========================================
def generate_otp():
    """Generates a random 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    """Sends the OTP via Gmail."""
    try:
        # Pulling credentials securely from Streamlit secrets
        sender_email = st.secrets["email_sender"]
        sender_password = st.secrets["email_password"]
        
        msg = EmailMessage()
        msg.set_content(f"Hello!\n\nYour EcoSolve verification code is: {otp}\n\nDo not share this code with anyone.")
        msg['Subject'] = 'EcoSolve Verification Code'
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        # Connect to Gmail's secure server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False