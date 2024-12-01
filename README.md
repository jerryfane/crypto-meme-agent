# Crypto Meme Agent - Marx Fren Monke

A GPT-4 powered agent that generates crypto-themed content. Originally created to power Marx Fren Monke ([@MarxFrenMonke](https://x.com/MarxFrenMonke)) - a hilariously unsuccessful Monke crypto trader from Mars.

## 🌟 Features

- Creates personality-driven crypto content using GPT-4
- Customizable agent personality through YAML configuration
- Automated X posts
- Web interface for content review and management
- Support for multiple content categories (trading, relationships, hobbies, etc.)

## 🛠️ Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL
- OpenAI API key
- Twitter API credentials
- Node.js and PM2 (for production deployment)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/jerryfane/crypto-meme-agent.git
cd crypto-meme-agent
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
cd database
docker compose up -d
```

## ⚙️ Configuration

1. Create a `.env` file in the root directory with these required credentials:
```env
# Twitter API Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Database Configuration (if different from default)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crypto_meme_agent
DB_USER=memeagent
DB_PASSWORD=memeagent
```

2. Configure your agent's personality by modifying `config/agent_config.yaml`. This file defines:
- Agent's name and characteristics
- System prompt for GPT-4
- Content templates and categories
- Twitter interaction settings
- Response formatting rules

Key sections to customize:
```yaml
agent:
  name: "Your Agent Name"
  nickname: "Nickname"
  base_location: "Location"
  character_traits:
    - "trait1"
    - "trait2"
  catchphrases:
    - "catchphrase1"
    - "catchphrase2"

prompt:
  system_message: |
    [Your agent's personality description]

templates:
  [customize template categories and formats]
```

## 🚀 Usage

### Development Environment

1. Start the database (if not already running):
```bash
cd database
docker compose up -d
```

2. Run the admin interface:
```bash
python src/admin/app.py
```
Access the admin interface at http://localhost:5000

3. Run the Twitter scheduler:
```bash
python src/twitter/scheduler.py
```

4. Run the meme generation agent:
```bash
python scripts/run_agent.py
```

### Production Deployment

1. Install PM2:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
sudo npm install pm2 -g
```

2. Create PM2 ecosystem file (ecosystem.config.js):
```javascript
module.exports = {
  apps: [
    {
      name: 'twitter-scheduler',
      script: '/root/crypto-meme-agent/venv/bin/python3',
      args: 'src/twitter/scheduler.py',
      interpreter: 'none',
      cwd: '/root/crypto-meme-agent'
    },
    {
      name: 'admin-app',
      script: '/root/crypto-meme-agent/venv/bin/python3',
      args: 'src/admin/app.py',
      interpreter: 'none',
      cwd: '/root/crypto-meme-agent'
    },
    {
      name: 'meme-agent',
      script: '/root/crypto-meme-agent/venv/bin/python3',
      args: 'scripts/run_agent.py',
      interpreter: 'none',
      cwd: '/root/crypto-meme-agent'
    }
  ]
}
```

3. Start all services:
```bash
cd crypto-meme-agent
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

4. Monitor processes:
```bash
pm2 status
pm2 logs
```

## 🔍 Monitoring

- Check PM2 process status: `pm2 status`
- View logs: `pm2 logs`
- Check database container: `docker ps`
- Monitor database logs: `docker logs crypto_meme_agent_db`

## 🚨 Troubleshooting

1. Database Connection Issues:
   - Verify Docker container is running: `docker ps`
   - Check database logs: `docker logs crypto_meme_agent_db`
   - Ensure correct database credentials in .env file

2. Twitter API Issues:
   - Verify Twitter API credentials in .env file
   - Check rate limits and API status

3. OpenAI API Issues:
   - Verify API key in .env file
   - Monitor API usage and limits

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the Viral Public License (VPL) - see the [LICENSE](LICENSE) file for details.

This means:
- The code must remain open source
- Any project using this code must also be released under VPL
- Commercial use is allowed but must follow the same open-source requirements
- Attribution must be maintained