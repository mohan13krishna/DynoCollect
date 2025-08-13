# Data Collection Web App with Authentication

A web application for collecting user contributions in various formats (text, audio, video, and images) using Flask, Streamlit, and Supabase. Features user authentication with Supabase Auth.

## Tech Stack

- **Frontend**: Streamlit (user interface)
- **Backend**: Flask
- **Database & Storage**: Supabase
- **Authentication**: Supabase Auth

## Project Structure
 
```
.
├── app/
│   ├── backend/
│   │   ├── app.py                # Flask backend with API endpoints and auth routes
│   │   ├── s3_uploader.py        # Supabase storage integration
│   │   └── example_upload.py     # Example script for file uploads
│   └── frontend/
│       └── app.py                # Streamlit frontend with auth UI
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── run.ps1                       # Script to run both servers
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Supabase

Edit the `.env` file and add your Supabase credentials:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 4. Run the application

On Windows, use the provided PowerShell script:

```bash
.\run.ps1
```

Or run the servers manually:

#### Start the Flask backend

```bash
python app/backend/app.py
```

#### Start the Streamlit frontend

```bash
streamlit run app/frontend/app.py
```

## Features

### Authentication

- **User Registration**: Create a new account with email and password
- **User Login**: Authenticate with email and password
- **Session Management**: Maintain user sessions securely
- **Logout**: End user sessions

### Data Collection

- **Text Submissions**: Submit text data
- **Audio Uploads**: Upload audio files (mp3, wav, ogg)
- **Video Uploads**: Upload video files (mp4, mov, avi)
- **Image Uploads**: Upload image files (jpg, jpeg, png, gif)

## Security

- Passwords are securely handled by Supabase Auth
- Authentication tokens are managed securely
- Session data is encrypted
- HTTPS recommended for production deployment

## API Endpoints

### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login a user
- `POST /auth/logout` - Logout a user
- `GET /auth/user` - Get current user information

### Data Collection Endpoints

- `POST /submit-text` - Submit text data
- `POST /upload-audio` - Upload audio files
- `POST /upload-video` - Upload video files
- `POST /upload-image` - Upload image files

The Flask server will start at http://localhost:5000

### 5. Run the Streamlit frontend

Open a new terminal and run:

```bash
cd app/frontend
streamlit run app.py
```

The Streamlit app will be available at http://localhost:8501

## API Endpoints

- **POST /submit-text** - Submit text data
- **POST /upload-audio** - Upload audio files
- **POST /upload-video** - Upload video files
- **POST /upload-image** - Upload image files

## Supabase Structure

### Database Table

```sql
create table contributions (
  id uuid primary key default gen_random_uuid(),
  text_data text,
  audio_url text,
  video_url text,
  image_url text,
  submitted_at timestamp with time zone default now()
);
```

### Storage Buckets

- `audio` - For audio file uploads
- `video` - For video file uploads
- `images` - For image file uploads
