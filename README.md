
# CurrencyBot Pro 💱

A powerful Telegram bot providing real-time currency exchange rates, conversions, and cryptocurrency data with a beautiful web dashboard.

## 🌟 Features

### 💱 Currency Features
- **169+ Supported Currencies** - Major world currencies, regional currencies, and precious metals
- **Real-time Exchange Rates** - Powered by top 5 trusted currency APIs
- **Smart API Fallback** - Multiple reliable data sources ensure 99.9% uptime
- **Accurate Conversions** - Enterprise-grade precision for all currency pairs
- **Live Updates** - Real-time rate monitoring with automatic updates

### 🪙 Cryptocurrency Support
- **Top Cryptocurrencies** - Bitcoin, Ethereum, and major altcoins
- **Live Price Tracking** - Real-time crypto market data
- **Portfolio Tracking** - Monitor your crypto investments
- **Market Trends** - Trending coins and market analysis

### 🤖 Telegram Bot Commands
- `/start` - Welcome message and quick access menu
- `/currency [CODE]` - Get exchange rates for specific currency
- `/convert [amount] [from] [to]` - Convert between any currencies
- `/allcurrencies` - View all supported currencies
- `/crypto` - Cryptocurrency prices and market data
- `/trending` - Trending cryptocurrencies
- `/realtime` - Live currency updates
- `/health` - API health status
- `/help` - Complete command reference

### 🌐 Web Dashboard
- **Beautiful Admin Panel** - Modern, responsive web interface
- **Real-time Statistics** - Live bot usage analytics
- **Currency Monitoring** - Live exchange rates display
- **Dark/Light Themes** - Customizable interface
- **Mobile Responsive** - Works perfectly on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd currencybot-pro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   ```

4. **Configure your bot**
   Edit `.env` file with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ADMIN_PASSWORD=your_secure_password
   FLASK_SECRET_KEY=your_secret_key_here
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

The bot will start running and the web dashboard will be available at `http://localhost:5000`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | ✅ Yes | - |
| `ADMIN_PASSWORD` | Web dashboard password | ✅ Yes | `admin123` |
| `FLASK_SECRET_KEY` | Flask session secret | ✅ Yes | `dev-secret-key` |
| `CURRENCY_API_KEY` | External API key (optional) | ❌ No | - |
| `DEBUG` | Enable debug mode | ❌ No | `False` |
| `LOG_LEVEL` | Logging level | ❌ No | `INFO` |

### Trusted Currency APIs

CurrencyBot Pro uses multiple trusted APIs for maximum reliability:

1. **ExchangeRate-API** (★★★★☆) - Primary free API
2. **Open Exchange Rates** (★★★★★) - Premium accuracy
3. **CurrencyFreaks** (★★★★☆) - Reliable backup
4. **ForexRateAPI** (★★★★☆) - Additional source
5. **Fixer.io** (★★★★☆) - APILayer powered

## 📊 Supported Currencies

### 🌎 Major World Currencies
USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR, MYR, and more...

### 🌏 Regional Currencies
Complete coverage of Asia-Pacific, European, African, and American currencies

### 💎 Precious Metals
- XAU (Gold)
- XAG (Silver)
- XPD (Palladium)
- XPT (Platinum)

### 🪙 Cryptocurrencies
Bitcoin (BTC), Ethereum (ETH), and top 100+ cryptocurrencies

## 🎯 Usage Examples

### Currency Conversion
```
/convert 100 USD EUR
💰 Trusted Currency Conversion

🇺🇸 100.00 USD
⬇️
🇪🇺 91.27 EUR

📈 Rate: 1 USD = 0.912700 EUR
🔒 Powered by Top 5 Trusted APIs
```

### Real-time Updates
```
/realtime
📈 Real-time Currency Monitor

🇺🇸 USD Base Rates:
🇪🇺 EUR: 0.9127 ⬆️ +0.15%
🇬🇧 GBP: 0.7854 ⬇️ -0.23%
🇯🇵 JPY: 157.32 ⬆️ +0.08%

🕐 12:34:56 UTC
📊 Showing 169 live rates
```

## 🛡️ Security Features

- **Secure API Management** - Multiple fallback sources
- **Data Encryption** - Sensitive data protection
- **Rate Limiting** - Anti-spam protection
- **Session Management** - Secure web dashboard access
- **Input Validation** - Protection against malicious inputs

## 📈 Performance

- **Sub-second Response** - Lightning-fast currency data
- **99.9% Uptime** - Reliable service with smart fallbacks
- **Caching System** - Optimized for high-volume usage
- **Concurrent Users** - Supports thousands of simultaneous users
- **Memory Efficient** - Optimized resource usage

## 🔧 Development

### Project Structure
```
currencybot-pro/
├── main.py              # Main bot application
├── dashboard.html       # Web dashboard template
├── login.html          # Admin login page
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── README.md         # This file
```

### Adding New Features

1. **New Currency APIs** - Add to `TRUSTED_CURRENCY_APIS` list
2. **Custom Commands** - Implement in bot handlers section
3. **Dashboard Features** - Modify HTML templates and Flask routes
4. **Database Integration** - Extend for user data persistence

### Testing

Test your bot locally:
```bash
# Test currency conversion
python -c "from main import trusted_api; print(trusted_api.convert_currency(100, 'USD', 'EUR'))"

# Test API health
python -c "from main import trusted_api; print([api['name'] for api in TRUSTED_CURRENCY_APIS if trusted_api.test_api_health(api)])"
```

## 📱 Bot Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and menu | `/start` |
| `/currency [CODE]` | Get exchange rates | `/currency EUR` |
| `/convert [amount] [from] [to]` | Convert currencies | `/convert 100 USD EUR` |
| `/allcurrencies` | List all currencies | `/allcurrencies` |
| `/crypto` | Cryptocurrency prices | `/crypto` |
| `/trending` | Trending crypto | `/trending` |
| `/realtime` | Live updates | `/realtime` |
| `/health` | API status | `/health` |
| `/help` | Command help | `/help` |

## 🌟 Pro Features

- **Enterprise-grade APIs** - Multiple trusted sources
- **Real-time Updates** - Live currency monitoring
- **Beautiful Dashboard** - Modern web interface
- **Mobile Optimized** - Perfect mobile experience
- **Cryptocurrency Support** - Complete crypto integration
- **Portfolio Tracking** - Investment monitoring
- **Alert System** - Price change notifications
- **Analytics Dashboard** - Comprehensive statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation** - Check this README for setup instructions
- **Issues** - Report bugs via GitHub Issues
- **Feature Requests** - Submit enhancement proposals
- **Community** - Join our Telegram support group

## 🎉 Acknowledgments

- Telegram Bot API for excellent bot platform
- Currency API providers for reliable data
- Flask framework for web dashboard
- Contributors and testers

---

**CurrencyBot Pro** - Your trusted currency companion! 💱✨

*Built with ❤️ for accurate, real-time currency data*
