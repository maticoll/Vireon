# Gmail Extension Backend

Backend service for the Gmail Chrome extension that processes emails and sends them to a webhook.

## 🚀 Deployment on Railway

### Prerequisites
- Railway account
- Google Cloud Console project with Gmail API enabled
- Make.com webhook URL

### Environment Variables

Create a `.env` file or set these variables in Railway:

```env
# Gmail API Configuration
GMAIL_CLIENT_ID=916833737676-2eu9kmrbdog7sv2911qroi4ipu60cdjt.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_gmail_client_secret_here
GMAIL_REDIRECT_URI=https://dmpbjeckkodecclfcnlcmpaifjnagmh.chromiumapp.org/oauth2callback.html

# Webhook Configuration
WEBHOOK_URL=https://hook.us2.make.com/vh2644shvy4dvq8kaq854ou7b8fqnzf0

# Server Configuration
PORT=3000
NODE_ENV=production

# JWT Secret (for token validation)
JWT_SECRET=your_secure_jwt_secret_here
```

### Deployment Steps

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Railway project:**
   ```bash
   railway init
   ```

4. **Set environment variables:**
   ```bash
   railway variables set GMAIL_CLIENT_ID=your_client_id
   railway variables set GMAIL_CLIENT_SECRET=your_client_secret
   railway variables set WEBHOOK_URL=your_webhook_url
   railway variables set JWT_SECRET=your_jwt_secret
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

### API Endpoints

- `GET /health` - Health check
- `POST /api/gmail/messages` - Get Gmail messages and send to webhook
- `POST /api/auth/validate` - Validate Gmail access token

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Run locally:**
   ```bash
   python app.py
   ```

### Docker Build

```bash
docker build -t gmail-extension-backend .
docker run -p 3000:3000 gmail-extension-backend
```

## 📁 Project Structure

```
Proyecto Gmail/
├── app.py              # Flask backend application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── railway.json       # Railway deployment config
├── manifest.json      # Chrome extension manifest
├── popup.html         # Extension popup
├── popup.js           # Extension frontend logic
├── background.js      # Extension background script
├── styles.css         # Extension styles
└── logo.png           # Extension icon
```

## 🔧 Configuration

### Google Cloud Console Setup

1. Enable Gmail API
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs
4. Download client secret

### Make.com Webhook

1. Create a new scenario in Make.com
2. Add a webhook trigger
3. Copy the webhook URL
4. Set it as `WEBHOOK_URL` environment variable

## 📝 License

MIT License 