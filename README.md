# 🚀 Intervue AI - Professional Career Platform

<div align="center">
  

  
**AI-Powered Interview Practice -  Resume Analysis -  Cold Email Optimization**
  


## 🎯 Project Overview

**Intervue AI** is a full-stack career development platform that helps users prepare for job interviews, optimize resumes, and craft compelling cold emails using cutting-edge AI. The platform features **real-time voice conversations** with animated AI avatars, **streaming analysis**, and **comprehensive feedback** with visual grading systems.[1]

Built with **Flask backend**, **Gemini 2.0 Flash** for intelligent analysis, and **ElevenLabs** for lifelike Text-to-Speech and Speech-to-Text, Intervue AI delivers a professional, production-ready experience.

## ✨ Key Features

- **Interview Practice** - Real-time voice conversations with "InterBlob" AI interviewer
- **Resume Analysis** - PDF/TXT upload with ATS optimization, content grading (A-F scale)
- **Cold Email Coach** - Subject line + body analysis with follow-up Q&A
- **Animated UI** - Speaking avatars with pulse effects and streaming indicators
- **Voice Integration** - Queue-based TTS with sentence-by-sentence streaming
- **Visual Grades** - Animated progress bars for metrics (ATS, Content Quality, etc.)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   AI Services   │
│  (HTML/JS/CSS)  │◄──►│   (Flask 5000)   │◄──►│                 │
│                 │    │                  │    │ • Gemini 2.0    │
│ • SPA Navigation│    │ • API Proxy      │    │ • ElevenLabs    │
│ • WebRTC Audio  │    │ • PDF Processing │    │   TTS/STT       │
│ • Streaming UI  │    │ • Streaming SSE  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites
```bash
Python 3.8+
Git
```

### 2. Clone & Setup
```bash
git clone <your-repo>
cd intervue-ai
pip install -r requirements.txt
```

### 3. Environment Variables
Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### 4. Install Dependencies
```bash
pip install flask flask-cors python-dotenv PyPDF2 requests
```

### 5. Run Server
```bash
python server.py
```
**Server runs at: http://localhost:5000**

## 🔧 Core Components

### Backend API Routes (`server.py`)

| Endpoint | Method | Purpose | Streaming |
|----------|--------|---------|-----------|
| `/api/analyze-resume` | POST | Resume analysis (PDF/TXT) | ❌ |
| `/api/analyze-resume/stream` | POST | **Streaming** resume feedback | ✅ |
| `/api/gemini` | POST | Gemini AI proxy | ❌ |
| `/api/gemini/stream` | POST | **Streaming** AI responses | ✅ |
| `/api/elevenlabs/tts` | POST | Text-to-Speech | ❌ |
| `/api/elevenlabs/tts/stream` | POST | **Streaming** TTS | ✅ |
| `/api/elevenlabs/stt` | POST | Speech-to-Text | ❌ |

### Frontend Features (`interview-trainer.html`)

- **Page Navigation**: Home, Interview, Resume, Email, How It Works, About
- **Real-time Streaming**: SSE for AI responses + sentence-by-sentence TTS
- **Voice Recording**: WebRTC + MediaRecorder API
- **Animated Avatars**: CSS pulse/scale effects during speech
- **Visual Grading**: Circular grades + animated metric bars[1]

## 🎮 How It Works

### 1. **Interview Mode**
```
User speaks → STT (ElevenLabs) → Gemini AI → Streaming Response → TTS Queue
```

### 2. **Resume Analysis**
```
PDF/TXT Upload → PyPDF2 Extraction → Gemini Analysis → Grade + Metrics + TTS
```

### 3. **Cold Email Review**
```
Subject + Body → Gemini Coach → Grade (Subject/Hook/CTA) → Follow-up Q&A
```

## 🛠️ File Structure

```
intervue-ai/
├── server.py              # Flask backend + API endpoints
├── interview-trainer.html # Frontend SPA (save as index.html)
├── .env                   # API keys
├── requirements.txt       # Python dependencies
└── README.md             # This file!
```

## 📱 UI Components

### InterBlob Avatar
```css
.avatar-circle.speaking {
  transform: scale(1.3);
  animation: pulse 2s infinite;
}
```

### Grade Cards
- **Resume**: ATS Score, Content Quality, Format & Design
- **Email**: Subject Line, Opening Hook, Call-to-Action

### Streaming Indicators
```css
.streaming-indicator {
  animation: pulse 1.5s ease-in-out infinite;
}
```

## 🔍 API Integration Details

### Gemini 2.0 Flash (`gemini-2.0-flash-exp`)
```
- Streaming: streamGenerateContent?alt=sse
- Temperature: 0.7
- Max Tokens: 4000
- Converts to OpenAI-compatible format
```

### ElevenLabs
```
TTS: eleven_turbo_v2 (fast streaming)
STT: scribe_v2 (high accuracy)
Voice: kdVjFjOXaqExaDvXZECX (default)
```

## 🎨 Customization

### Change Voice
```javascript
const VOICE_ID = 'YOUR_ELEVENLABS_VOICE_ID';
```

### Update AI Model
```python
# server.py line ~50
'https://generativelanguage.googleapis.com/v1beta/models/YOUR_MODEL'
```

### Brand Colors
```css
:root {
  --primary: #2563eb;
  --accent: #dc2626;
}
```

## 🚀 Production Deployment

```bash
# Gunicorn + Nginx
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# Docker (coming soon)
docker build -t intervue-ai .
docker run -p 5000:5000 intervue-ai
```

## 📈 Future Enhancements

- [ ] Multi-language support
- [ ] Video recording analysis
- [ ] Team collaboration
- [ ] Premium voices/models
- [ ] Mobile PWA
- [ ] Analytics dashboard

## 👨‍💻 About the Developer

**Thomas de Chillaz**  
🎓 CentraleSupélec -  ESSEC AIDAMS  
💻 Full-stack AI Developer  
🌍 Helping you land dream jobs worldwide[1]

<div align="center">

**⭐ Star on GitHub -  👨‍💼 Connect on LinkedIn -  🚀 Try Intervue AI Now!**



<p align="center">
  <em>© 2025 Intervue AI. Powered by Gemini 2.0 Flash & ElevenLabs</em>
</p>

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/51427386/1cae6bf1-edb0-4abe-b53d-aa2598fde6a9/paste.txt)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.
