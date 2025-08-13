import streamlit as st
import requests
import json
import time

# Configure API URL
API_URL = "https://dynocollect.onrender.com"

# Set page config
st.set_page_config(
    page_title="Swecha Media Upload",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "show_login" not in st.session_state:
    st.session_state.show_login = True

# Function to handle login
def login(email, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            st.session_state.authenticated = True
            st.session_state.user = user_data
            return True, "Login successful!"
        else:
            error_msg = response.json().get("error", "Login failed. Please check your credentials.")
            return False, error_msg
    except Exception as e:
        return False, f"Error: {str(e)}"

# Function to handle registration
def register(email, password, confirm_password):
    if password != confirm_password:
        return False, "Passwords do not match."
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            st.session_state.show_login = True
            return True, "Registration successful! Please login."
        else:
            error_msg = response.json().get("error", "Registration failed.")
            return False, error_msg
    except Exception as e:
        return False, f"Error: {str(e)}"

# Function to handle logout
def logout():
    try:
        st.session_state.authenticated = False
        st.session_state.user = None
        return True, "Logout successful!"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Main app
st.title("Swecha Media Upload")

# Check if user is authenticated
if not st.session_state.authenticated:
    # Show login/register forms
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.show_login:
            st.header("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", key="login_button"):
                success, message = login(email, password)
                if success:
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
                    
            if st.button("Need to register?", key="goto_register"):
                st.session_state.show_login = False
                st.experimental_rerun()
        else:
            st.header("Register")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Register", key="register_button"):
                success, message = register(email, password, confirm_password)
                if success:
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
                    
            if st.button("Already have an account?", key="goto_login"):
                st.session_state.show_login = True
                st.experimental_rerun()

else:
    # User is authenticated, show the main app
    # Display user info and logout button in sidebar
    with st.sidebar:
        st.write(f"Logged in as: {st.session_state.user.get('email')}")
        if st.button("Logout"):
            success, message = logout()
            if success:
                st.success(message)
                st.experimental_rerun()
            else:
                st.error(message)
    
    # Create a radio button for different submission types
    submission_type = st.radio("Select submission type", ["Text", "Audio", "Video", "Image"])

    # Text submission form
    if submission_type == "Text":
        st.header("Submit Text")
        text_data = st.text_area("Enter your text here", height=200)

        if st.button("Submit Text"):
            if text_data:
                try:
                    response = requests.post(
                        f"{API_URL}/submit-text",
                        json={"text_data": text_data},
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 201:
                        st.success("Text submitted successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter some text before submitting.")

    # Audio upload form
    elif submission_type == "Audio":
        st.header("Upload Audio")
        st.info("✨ Now with high-speed S3 uploads - supports files up to 500MB!")
        st.warning("⚠️ Files larger than 500MB may cause upload errors due to storage limitations.")
        st.warning("⚠️ Files between 50MB and 500MB may take longer to upload and could occasionally fail due to Supabase Storage limitations.")
        audio_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "ogg"])

        if audio_file is not None:
            file_size_mb = len(audio_file.getvalue()) / (1024 * 1024)
            st.info(f"File size: {file_size_mb:.2f} MB")

            est_seconds = file_size_mb / 20
            if est_seconds < 60:
                est_time = f"{est_seconds:.1f} seconds"
            else:
                est_time = f"{est_seconds/60:.1f} minutes"
            st.info(f"Estimated upload time: {est_time} (at ~20MB/s)")

        if st.button("Submit Audio"):
            if audio_file is not None:
                file_size_mb = len(audio_file.getvalue()) / (1024 * 1024)
                if file_size_mb > 500:
                    st.error(f"File size ({file_size_mb:.2f} MB) exceeds the 500 MB limit. Please select a smaller file.")
                else:
                    try:
                        with st.spinner("Uploading audio... Please wait."):
                            files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
                            response = requests.post(f"{API_URL}/upload-audio", files=files, timeout=600)

                        if response.status_code == 201:
                            result = response.json()
                            st.success("✅ Audio uploaded successfully!")

                            upload_time = result.get('upload_time_seconds', 0)
                            upload_speed = result.get('upload_speed_mbps', 0)

                            metrics_col1, metrics_col2 = st.columns(2)
                            with metrics_col1:
                                st.metric("Upload Time", f"{upload_time:.2f} seconds")
                            with metrics_col2:
                                st.metric("Upload Speed", f"{upload_speed:.2f} MB/s")

                            st.subheader("Audio Details")
                            st.markdown(f"**URL:** {result.get('url', 'N/A')}")
                            st.json(result.get('data', {}))
                        else:
                            error_msg = response.json().get('error', 'Unknown error')
                            st.error(f"Upload failed: {error_msg}")
                    except requests.exceptions.Timeout:
                        st.error("Upload timed out. The server took too long to respond.")
                        st.info("Try uploading a smaller file or check your internet connection.")
                    except Exception as e:
                        st.error(f"Upload error: {str(e)}")
            else:
                st.warning("Please select an audio file before submitting.")

    # Video upload form
    elif submission_type == "Video":
        st.header("Upload Video")
        st.info("✨ Now with high-speed S3 uploads - supports files up to 500MB!")
        st.warning("⚠️ Files larger than 500MB may cause upload errors due to storage limitations.")
        video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

        if video_file is not None:
            file_size_mb = len(video_file.getvalue()) / (1024 * 1024)
            st.info(f"File size: {file_size_mb:.2f} MB")
    
            est_seconds = file_size_mb / 20
            if est_seconds < 60:
                est_time = f"{est_seconds:.1f} seconds"
            else:
                est_time = f"{est_seconds/60:.1f} minutes"
            st.info(f"Estimated upload time: {est_time} (at ~20MB/s)")
    
        if st.button("Submit Video"):
            if video_file is not None:
                file_size_mb = len(video_file.getvalue()) / (1024 * 1024)
                if file_size_mb > 500:
                    st.error(f"File size ({file_size_mb:.2f} MB) exceeds the 500 MB limit. Please select a smaller file.")
                else:
                    try:
                        with st.spinner("Uploading video... Please wait."):
                            files = {"file": (video_file.name, video_file.getvalue(), video_file.type)}
                            response = requests.post(f"{API_URL}/upload-video", files=files, timeout=600)
    
                        if response.status_code == 201:
                            result = response.json()
                            st.success("✅ Video uploaded successfully!")
    
                            upload_time = result.get('upload_time_seconds', 0)
                            upload_speed = result.get('upload_speed_mbps', 0)
    
                            metrics_col1, metrics_col2 = st.columns(2)
                            with metrics_col1:
                                st.metric("Upload Time", f"{upload_time:.2f} seconds")
                            with metrics_col2:
                                st.metric("Upload Speed", f"{upload_speed:.2f} MB/s")
    
                            st.subheader("Video Details")
                            st.markdown(f"**URL:** {result.get('url', 'N/A')}")
                            st.json(result.get('data', {}))
                        else:
                            error_msg = response.json().get('error', 'Unknown error')
                            st.error(f"Upload failed: {error_msg}")
                    except requests.exceptions.Timeout:
                        st.error("Upload timed out. The server took too long to respond.")
                        st.info("Try uploading a smaller file or check your internet connection.")
                    except Exception as e:
                        st.error(f"Upload error: {str(e)}")
            else:
                st.warning("Please select a video file before submitting.")

    # Image upload form
    elif submission_type == "Image":
        st.header("Upload Image")
        st.info("✨ Now with high-speed S3 uploads - supports files up to 500MB!")
        st.warning("⚠️ Files larger than 500MB may cause upload errors due to storage limitations.")
        image_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png", "gif"])

        if image_file is not None:
            file_size_mb = len(image_file.getvalue()) / (1024 * 1024)
            st.info(f"File size: {file_size_mb:.2f} MB")

            est_seconds = file_size_mb / 20
            if est_seconds < 60:
                est_time = f"{est_seconds:.1f} seconds"
            else:
                est_time = f"{est_seconds/60:.1f} minutes"
            st.info(f"Estimated upload time: {est_time} (at ~20MB/s)")

        if st.button("Submit Image"):
            if image_file is not None:
                file_size_mb = len(image_file.getvalue()) / (1024 * 1024)
                if file_size_mb > 500:
                    st.error(f"File size ({file_size_mb:.2f} MB) exceeds the 500 MB limit. Please select a smaller file.")
                else:
                    try:
                        with st.spinner("Uploading image... Please wait."):
                            files = {"file": (image_file.name, image_file.getvalue(), image_file.type)}
                            response = requests.post(f"{API_URL}/upload-image", files=files, timeout=600)

                        if response.status_code == 201:
                            result = response.json()
                            st.success("✅ Image uploaded successfully!")

                            upload_time = result.get('upload_time_seconds', 0)
                            upload_speed = result.get('upload_speed_mbps', 0)

                            metrics_col1, metrics_col2 = st.columns(2)
                            with metrics_col1:
                                st.metric("Upload Time", f"{upload_time:.2f} seconds")
                            with metrics_col2:
                                st.metric("Upload Speed", f"{upload_speed:.2f} MB/s")

                            st.subheader("Image Details")
                            st.markdown(f"**URL:** {result.get('url', 'N/A')}")
                            st.json(result.get('data', {}))
                        else:
                            error_msg = response.json().get('error', 'Unknown error')
                            st.error(f"Upload failed: {error_msg}")
                    except requests.exceptions.Timeout:
                        st.error("Upload timed out. The server took too long to respond.")
                        st.info("Try uploading a smaller file or check your internet connection.")
                    except Exception as e:
                        st.error(f"Upload error: {str(e)}")
            else:
                st.warning("Please select an image file before submitting.")
    else:
        st.warning("Please select a submission type from the sidebar.")
