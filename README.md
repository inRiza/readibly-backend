# 📘 Readibly Backend

## 🤝 Tim Hackteunnn

### Anggota:
- Muhammad Fadhlan Karimuddin
- Muhammad Rizain Firdaus
- Stefanny Josefina Santono

## 💡 Brief Explanation
Readibly Backend adalah layanan unggulan yang mengintegrasikan pemrosesan PDF, pelacakan mata, dan konversi teks ke suara. Produk ini dirancang untuk meningkatkan aksesibilitas informasi dengan API yang mudah diintegrasikan dan fitur canggih seperti analisis mata secara real-time.

## 🌐 Frontend Repository
[Readibly/readibly-frontend](https://github.com/Readibly/readibly-frontend)

## 🔍 Features

- PDF parsing and text extraction
- Eye tracking using webcam
- Text-to-speech conversion
- RESTful API endpoints

## Prerequisites

- Python 3.8 or higher
- Webcam (for eye tracking)
- OpenCV dependencies

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

1. Start the FastAPI server:
```bash
python main.py
```

2. The server will start at `http://localhost:8000`

## API Endpoints

### PDF Processing
- `POST /api/upload-pdf`: Upload and parse PDF files
- Returns extracted text content organized by pages

### Eye Tracking
- `POST /api/start-eye-tracking`: Start eye tracking
- `POST /api/stop-eye-tracking`: Stop eye tracking
- Returns gaze tracking data

### Text-to-Speech
- `POST /api/text-to-speech`: Convert text to speech
- Returns path to generated audio file

## Directory Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── services/           # Service modules
│   ├── pdf_parser.py   # PDF parsing service
│   ├── eye_tracker.py  # Eye tracking service
│   └── text_to_speech.py # Text-to-speech service
└── static/             # Static files
    └── audio/          # Generated audio files
```

## Notes

- The eye tracking feature requires a webcam
- PDF parsing supports standard PDF files
- Text-to-speech audio files are automatically cleaned up after 24 hours