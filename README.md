# 🤖 AI HR Recruiter - Zero Budget Demo App

Automate bulk hiring with resume extraction, messaging, and candidate management.

## ✨ Features

- 📄 **Resume Upload** - Upload CV screenshots (PNG/JPG/PDF)
- 🤖 **AI Extraction** - Auto-extract candidate details
- 📧 **Email & SMS** - Simulated messaging (zero cost)
- 📊 **Candidate Management** - Track status, schedule interviews
- 🔐 **Authentication** - Secure login system
- 💼 **Job Settings** - Configure job details
- 📱 **Messages Log** - View all sent messages

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on: `http://127.0.0.1:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on: `http://localhost:3000`

### Default Login

- **Username:** `admin`
- **Password:** `admin123`

## 📁 Project Structure

```
ai-hr-recruiter/
├── backend/
│   ├── app.py              # Flask backend
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── candidates.db       # SQLite database (auto-created)
│
└── frontend/
    ├── src/
    │   ├── App.js          # Main React app
    │   ├── components/     # React components
    │   └── index.js        # Entry point
    ├── package.json        # Node dependencies
    └── public/             # Static files
```

## 🌐 Deploy as Website

### Option 1: Netlify (Frontend) + Railway (Backend)

#### Deploy Frontend to Netlify:

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Go to [netlify.com](https://netlify.com)
3. Drag & drop the `build` folder
4. Get your URL: `https://your-app.netlify.app`

#### Deploy Backend to Railway:

1. Go to [railway.app](https://railway.app)
2. Create new project
3. Upload `backend` folder
4. Add environment variables (if needed)
5. Get your URL: `https://your-app.railway.app`

#### Connect Frontend to Backend:

Update `frontend/src/App.js`:
```javascript
const API_URL = 'https://your-app.railway.app'; // Your Railway URL
```

### Option 2: Vercel (Frontend) + Render (Backend)

#### Deploy Frontend to Vercel:

```bash
cd frontend
npm install -g vercel
vercel --prod
```

#### Deploy Backend to Render:

1. Go to [render.com](https://render.com)
2. Create Web Service
3. Connect GitHub or upload files
4. Auto-deploys!

### Option 3: Heroku (Full Stack)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create ai-hr-recruiter

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku master
```

## 📱 Create Desktop App

### Using Electron:

1. Install Electron:
```bash
cd frontend
npm install --save-dev electron electron-builder
```

2. Add to `package.json`:
```json
{
  "main": "public/electron.js",
  "scripts": {
    "electron": "electron .",
    "electron-pack": "electron-builder"
  }
}
```

3. Create `public/electron.js`:
```javascript
const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800
  });
  win.loadFile('build/index.html');
}

app.whenReady().then(createWindow);
```

4. Build:
```bash
npm run build
npm run electron-pack
```

Result: `.exe` (Windows) or `.app` (Mac) file!

## 🔧 Configuration

### Environment Variables (Backend)

Create `backend/.env`:
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key (optional)
```

### Database

SQLite database (`candidates.db`) is auto-created on first run.

Tables:
- `users` - Authentication
- `candidates` - Candidate data
- `job_settings` - Job configuration

## 📊 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/check-auth` - Check auth status

### Candidates
- `POST /api/upload-resume` - Upload CV
- `POST /api/save-candidate` - Save candidate
- `GET /api/candidates` - Get all candidates
- `POST /api/update-candidate` - Update candidate

### Messaging
- `POST /api/send-message` - Send email/SMS
- `GET /api/message-log` - Get message history

### Job Settings
- `GET /api/job-settings` - Get job settings
- `POST /api/job-settings` - Update job settings

## 🎯 Demo Mode

**All messages are SIMULATED** (zero cost):
- ✅ No Gmail credentials needed
- ✅ No Twilio SMS costs
- ✅ All messages logged to `sent_messages.log`
- ✅ View in Messages tab
- ✅ Perfect for testing

## 🔐 Security

- Password hashing with Werkzeug
- Session-based authentication
- CORS protection
- SQL injection prevention
- Input validation

## 📝 License

MIT License - Free to use and modify

## 🤝 Support

For issues or questions, create an issue on GitHub.

## 🎉 Credits

Built with:
- Flask (Backend)
- React (Frontend)
- SQLite (Database)
- TailwindCSS (Styling)
- shadcn/ui (Components)
