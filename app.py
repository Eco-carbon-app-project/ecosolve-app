import streamlit as st
import datetime
import json

# Import the other scripts (we will build these next!)
import auth
import database as db
import carbon_data as cd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="EcoSolve - Dynamic Footprint", page_icon="🌍", layout="wide")

# Initialize database on startup
db.init_db()

# --- 2. SESSION STATE (App Memory) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# "Shopping Carts" for the Used and Avoided items
if 'used_cart' not in st.session_state:
    st.session_state['used_cart'] = []
if 'avoided_cart' not in st.session_state:
    st.session_state['avoided_cart'] = []

# --- 3. NAVIGATION ---
st.sidebar.title("🌱 EcoSolve Tracker")

if not st.session_state['logged_in']:
    menu = ["Login", "Sign Up", "Forgot Password"]
else:
    st.sidebar.success(f"Welcome, {st.session_state['username']}!")
    menu = ["Log Actions", "Leaderboard", "My Profile", "Logout"]

choice = st.sidebar.radio("Navigation", menu)

# --- 4. APP PAGES ---

# ==========================================
# PAGE: SIGN UP (OTP + SECURITY QUESTION)
# ==========================================
if choice == "Sign Up":
    st.title("Create an Account")
    st.write("Join the campus leaderboard!")
    
    # 1. Basic Details
    new_user = st.text_input("Username")
    new_email = st.text_input("Email Address")
    new_password = st.text_input("Password", type="password")
    block = st.selectbox("Campus Block / Club", ["Block A", "Block B", "Hostel 1", "Hostel 2", "Faculty", "Eco Club"])
    
    st.markdown("---")
    
    # 2. Security Question (For Password Resets)
    st.write("**Security Question (For Password Reset)**")
    sec_q = st.selectbox("Choose a question", ["What is your pet's name?", "What city were you born in?", "What is your favorite color?"])
    sec_a = st.text_input("Answer")
    
    # Session state to manage OTP flow
    if 'otp_sent' not in st.session_state:
        st.session_state['otp_sent'] = False
        st.session_state['generated_otp'] = ""
        
    st.markdown("---")
    
    # Step 1: Send the Code
    if not st.session_state['otp_sent']:
        if st.button("Send Verification Code"):
            # Ensure ALL fields, including the security answer, are filled out first
            if new_user and new_email and new_password and sec_a:
                with st.spinner("Sending code..."):
                    st.session_state['generated_otp'] = auth.generate_otp()
                    success = auth.send_otp_email(new_email, st.session_state['generated_otp'])
                    if success:
                        st.session_state['otp_sent'] = True
                        st.rerun()
                    else:
                        st.error("Error sending email. Please check your internet connection or email spelling.")
            else:
                st.warning("Please fill out all fields (including the security answer) before sending the code.")
                
    # Step 2: Verify and Create Account
    else:
        st.success(f"OTP sent to {new_email}!")
        entered_otp = st.text_input("Enter 6-digit OTP")
        
        if st.button("Verify & Create Account"):
            if entered_otp == st.session_state['generated_otp']:
                # WE PASS THE REAL DATA HERE (sec_q and sec_a)! No more dummy data.
                success, msg = auth.register_user(new_user, new_email, new_password, block, sec_q, sec_a)
                if success:
                    st.success(msg + " You can now go to Login.")
                    # Reset state for next time
                    st.session_state['otp_sent'] = False 
                else:
                    st.error(msg)
            else:
                st.error("Invalid OTP. Please try again.")
                
        if st.button("Cancel / Edit Details"):
            st.session_state['otp_sent'] = False
            st.rerun()
# ==========================================
# PAGE: LOGIN
# ==========================================
elif choice == "Login":
    st.title("Login")
    # Flexible login: Email OR Username
    identifier = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        success, result = auth.login_user(identifier, password)
        if success:
            st.session_state['logged_in'] = True
            st.session_state['username'] = result  # auth will return the correct username
            st.rerun()
        else:
            st.error(result)

# ==========================================
# PAGE: FORGOT PASSWORD
# ==========================================
elif choice == "Forgot Password":
    st.title("Reset Password")
    identifier = st.text_input("Enter your Username or Email")
    
    if st.button("Find Account"):
        success, q_or_msg = auth.get_security_question(identifier)
        if success:
            st.session_state['reset_id'] = identifier
            st.session_state['sec_q'] = q_or_msg
        else:
            st.error(q_or_msg)
            
    if 'sec_q' in st.session_state:
        st.info(f"Security Question: {st.session_state['sec_q']}")
        answer = st.text_input("Answer")
        new_password = st.text_input("New Password", type="password")
        
        if st.button("Reset Password"):
            success, msg = auth.reset_password(st.session_state['reset_id'], answer, new_password)
            if success:
                st.success(msg)
                del st.session_state['sec_q']
            else:
                st.error(msg)

# ==========================================
# PAGE: LOG ACTIONS (The Dynamic Core)
# ==========================================
elif choice == "Log Actions":
    st.title("⚖️ Dynamic Impact Calculator")
    st.write("Add ALL the things you used and ALL the things you avoided today using the ➕ buttons.")
    
    # Catch errors just in case carbon_data isn't fully ready yet
    try:
        categories = cd.get_all_categories()
    except:
        categories = ["Loading..."]

    col1, col2 = st.columns(2)
    
    # --- SECTION A: WHAT I USED ---
    with col1:
        st.subheader("🔴 What I Used (Emissions)")
        try:
            u_cat = st.selectbox("Category", categories, key="u_cat")
            u_item = st.selectbox("Item/Action", cd.get_items(u_cat), key="u_item")
        except:
            u_cat, u_item = "N/A", "N/A"
            
        u_qty = st.number_input("Quantity (floors, bottles, km, etc.)", min_value=1.0, value=1.0, step=1.0, key="u_qty")
        
        if st.button("➕ Add to Used List", use_container_width=True):
            st.session_state['used_cart'].append({"category": u_cat, "item": u_item, "qty": u_qty})
            
        st.markdown("---")
        st.markdown("**📝 Your 'Used' List:**")
        for idx, item in enumerate(st.session_state['used_cart']):
            st.write(f"- {item['qty']}x {item['item']} ({item['category']})")
            
        if st.button("🗑️ Clear Used List"):
            st.session_state['used_cart'] = []
            st.rerun()

    # --- SECTION B: WHAT I AVOIDED ---
    with col2:
        st.subheader("🟢 What I Avoided (Savings)")
        try:
            a_cat = st.selectbox("Category", categories, key="a_cat")
            a_item = st.selectbox("Item/Action", cd.get_items(a_cat), key="a_item")
        except:
            a_cat, a_item = "N/A", "N/A"
            
        a_qty = st.number_input("Quantity (floors, bottles, km, etc.)", min_value=1.0, value=1.0, step=1.0, key="a_qty")
        
        if st.button("➕ Add to Avoided List", use_container_width=True):
            st.session_state['avoided_cart'].append({"category": a_cat, "item": a_item, "qty": a_qty})
            
        st.markdown("---")
        st.markdown("**📝 Your 'Avoided' List:**")
        for idx, item in enumerate(st.session_state['avoided_cart']):
            st.write(f"- {item['qty']}x {item['item']} ({item['category']})")
            
        if st.button("🗑️ Clear Avoided List"):
            st.session_state['avoided_cart'] = []
            st.rerun()

    st.markdown("---")
    
    # --- SUBMIT & CALCULATE ---
    if st.button("🚀 Calculate & Submit Log", type="primary"):
        if not st.session_state['used_cart'] and not st.session_state['avoided_cart']:
            st.warning("Please add at least one item to either list before submitting.")
        else:
            try:
                # Math handled by carbon_data script
                net_saved, points, emitted, avoided = cd.calculate_impact(st.session_state['used_cart'], st.session_state['avoided_cart'])
                
                st.write(f"**Total Carbon Emitted:** {emitted:.3f} kg CO2")
                st.write(f"**Total Carbon Avoided:** {avoided:.3f} kg CO2")
                
                if net_saved > 0:
                    st.success(f"🌍 **Net Carbon Saved:** {net_saved:.3f} kg CO2")
                    st.info(f"🏆 **Points Earned:** {points}")
                    st.balloons()
                else:
                    st.error(f"⚠️ **Net Impact:** You emitted {abs(net_saved):.3f} kg CO2 more than you avoided. (0 Points)")
                
                # Save to database
                db.save_log(
                    username=st.session_state['username'],
                    date=str(datetime.date.today()),
                    used_json=json.dumps(st.session_state['used_cart']),
                    avoided_json=json.dumps(st.session_state['avoided_cart']),
                    net_saved=net_saved,
                    points=points
                )
                
                # Clear carts after successful save
                st.session_state['used_cart'] = []
                st.session_state['avoided_cart'] = []
            except Exception as e:
                st.error("Error calculating. Make sure carbon_data and database scripts are ready!")

# ==========================================
# PAGE: LEADERBOARD
# ==========================================
elif choice == "Leaderboard":
    st.title("🏆 Campus Leaderboard")
    try:
        df = db.get_leaderboard()
        if not df.empty:
            # Show Top 3 winners beautifully
            cols = st.columns(3)
            if len(df) >= 1: cols[0].metric("🥇 1st Place", df.iloc[0]["Username"], f"{df.iloc[0]['Total Points']} pts")
            if len(df) >= 2: cols[1].metric("🥈 2nd Place", df.iloc[1]["Username"], f"{df.iloc[1]['Total Points']} pts")
            if len(df) >= 3: cols[2].metric("🥉 3rd Place", df.iloc[2]["Username"], f"{df.iloc[2]['Total Points']} pts")
            
            st.dataframe(df, use_container_width=True)
            
            st.subheader("🏫 Block Battles")
            block_df = db.get_block_leaderboard()
            st.bar_chart(block_df.set_index('Block'))
        else:
            st.info("No data yet. Go log some actions to be number one!")
    except:
        st.warning("Database not connected yet.")

# ==========================================
# PAGE: PROFILE & LOGOUT
# ==========================================
elif choice == "My Profile":
    st.title("👤 Edit Profile")
    try:
        profile = db.get_user_profile(st.session_state['username'])
        if profile:
            new_email = st.text_input("Email", value=profile['email'])
            # Ensure index doesn't crash if block is missing
            blocks = ["Block A", "Block B", "Hostel 1", "Hostel 2", "Faculty", "Eco Club"]
            current_idx = blocks.index(profile['block']) if profile['block'] in blocks else 0
            new_block = st.selectbox("Campus Block", blocks, index=current_idx)
            
            if st.button("Update Profile"):
                success, msg = db.update_profile(st.session_state['username'], new_email, new_block)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    except:
        st.warning("Database not connected yet.")

elif choice == "Logout":
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.session_state['used_cart'] = []
    st.session_state['avoided_cart'] = []
    st.rerun()