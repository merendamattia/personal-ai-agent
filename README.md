# 📝 Personal AI Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/merendamattia/personal-ai-agent?label=release)](https://github.com/merendamattia/personal-ai-agent/releases)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)

An intelligent AI agent that generates detailed and professional Amazon product reviews, sales listings, optimizes prompts using KERNEL principles, and rewrites emails with different tones. Powered by OpenAI and Google AI models with advanced web scraping and content analysis capabilities.

## ✨ Features

- 🤖 **Multi-Provider Support** - Works with OpenAI (GPT) and Google (Gemini) models
- 📝 **Product Reviews** - Generate detailed and professional Amazon product reviews
- 💼 **Sales Listings** - Create persuasive sales listings for platforms like eBay, Subito, or Facebook Marketplace
- ✨ **Prompt Optimizer** - Rewrite and optimize prompts following KERNEL framework principles
- 📧 **Email Rewriter** - Rewrite emails with different tones (formal, friendly, diplomatic, assertive, empathetic)
- 📋 **Official Report Rewriter** - Transform informal reports into professional technical documents
- 🔗 **Direct Link Processing** - Paste an Amazon product link and get instant output
- 📱 **Telegram Bot** - Interact with all agents directly through Telegram
- 🌐 **Web Content Extraction** - Advanced web fetching with intelligent token management
- 📊 **Smart Token Management** - Automatic content truncation for optimal performance with token counting
- 💬 **Multi-Tool Agent System** - Uses DataPizza framework for powerful agent capabilities
- 🛡️ **Error Handling** - Robust error handling and logging throughout
- ⚙️ **Flexible Configuration** - Easy switching between providers and models
- 🔄 **URL Expansion** - Automatic expansion of shortened Amazon URLs (amzn.to, a.co, etc.)

## 📋 Requirements

- **Python 3.11+**
- **AI Provider API Key** (OpenAI or Google)
- **Telegram Bot Token** (optional, only for Telegram bot mode)

## 🚀 Getting Started

### Installation

1. **Clone the repository and enter the directory:**
   ```bash
   git clone https://github.com/merendamattia/personal-ai-agent.git
   cd personal-ai-agent
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   conda create --name personal-ai-agent-env python=3.11.13
   conda activate personal-ai-agent-env
   ```

   Or using venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred AI provider API key
   ```

   **For Google (default provider):**
   ```env
   GOOGLE_API_KEY=your_api_key_here
   GOOGLE_MODEL=gemini-2.5-flash
   TELEGRAM_BOT_TOKEN=your_telegram_token_here  # Optional
   ```

   **For OpenAI:**
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   TELEGRAM_BOT_TOKEN=your_telegram_token_here  # Optional
   ```

### Running the Application

#### CLI - Generate a review, sales listing, optimize a prompt, or rewrite an email:

```bash
# Generate a review using default provider (Google)
python app.py https://www.amazon.com/your-product-link

# Generate a sales listing
python app.py --type listing https://www.amazon.com/your-product-link

# Optimize a prompt following KERNEL principles
python app.py --type optimize-prompt "Your prompt text here"

# Rewrite an email
python app.py --type rewrite-email "Your email text here"

# Use OpenAI provider explicitly
python app.py --provider openai https://www.amazon.com/your-product-link

# Generate listing with OpenAI
python app.py --type listing --provider openai https://www.amazon.com/your-product-link

# Optimize prompt with OpenAI
python app.py --type optimize-prompt --provider openai "Your prompt text here"

# Rewrite email with OpenAI
python app.py --type rewrite-email --provider openai "Your email text here"
```

**Output Types:**
- `review` (default) - Generate Amazon product reviews
- `listing` - Create sales listings for secondary markets
- `optimize-prompt` - Rewrite prompts using KERNEL structure
- `rewrite-email` - Rewrite emails with different tones
- `rewrite-report` - Rewrite official reports with technical language

**Supported providers:**
- `google` (default) - Uses Google's Gemini models
- `openai` - Uses OpenAI's GPT models

**Token Counting:**
All operations display the number of tokens used in the input prompt for cost estimation and performance monitoring.

#### Telegram Bot - Interactive chat interface:
Quick start:
```bash
# 1. Update .env with TELEGRAM_BOT_TOKEN and your preferred provider credentials
# 2. Run the bot with default provider (Google)
python telegram_bot.py

# Or specify a different provider
python telegram_bot.py --provider openai
```

Then open Telegram, find your bot, and start using it!


### Docker

**Telegram Bot Mode:**
```bash
docker build -t personal-ai-agent:local .
docker run --env-file .env --restart unless-stopped personal-ai-agent:local
```

**Docker Compose (easiest):**
```bash
# Run Telegram Bot
docker compose up
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Commit conventions
- Pull request process

## Troubleshooting

### Common Issues

**"API key not found in .env"**
- Ensure your `.env` file exists in the project root directory
- Verify you have configured the credentials for your chosen provider
- Check that the environment variable names are correct

**"Unsupported provider" error**
- Ensure you're using a valid provider: `openai` or `google`
- Verify that the corresponding API credentials are set in your `.env` file

**"Connection timeout"**
- Verify your internet connection
- Check the service status for your provider (OpenAI or Google)

**"Rate limit exceeded"**
- Wait a moment before retrying
- Consider using a more cost-effective model variant

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## 📞 Support

For issues, feature requests, or questions:
- Open an [issue on GitHub](https://github.com/merendamattia/personal-ai-agent/issues)

## 🙏 Acknowledgments

- Built with [DataPizza AI Framework](https://datapizza.ai)
- Powered by [OpenAI](https://openai.com)
