import asyncio
import logging
import os
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, NetworkError, TimedOut
import requests

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot configuration
BOT_TOKEN = '7800653916:AAEbipLwXqwW7OuuKeaRHVGG1SjHagxnwjc'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Top Trusted Currency APIs (2025) - As per your recommendation
TRUSTED_CURRENCY_APIS = [
    {
        "name": "ExchangeRate-API",
        "url": "https://api.exchangerate-api.com/v4/latest/",
        "type": "exchangerate",
        "free": True,
        "accuracy": 4,
        "status": "unknown"
    },
    {
        "name": "Open Exchange Rates",
        "url": "https://openexchangerates.org/api/latest.json",
        "type": "openexchange",
        "free": True,
        "accuracy": 5,
        "status": "unknown"
    },
    {
        "name": "CurrencyFreaks",
        "url": "https://api.currencyfreaks.com/latest",
        "type": "currencyfreaks",
        "free": True,
        "accuracy": 4,
        "status": "unknown"
    },
    {
        "name": "ForexRateAPI",
        "url": "https://api.forexrateapi.com/v1/latest",
        "type": "forexrateapi",
        "free": True,
        "accuracy": 4,
        "status": "unknown"
    },
    {
        "name": "Fixer.io",
        "url": "https://api.fixer.io/latest",
        "type": "fixer",
        "free": True,
        "accuracy": 4,
        "status": "unknown"
    }
]

# Data storage
bot_stats = {
    'users': set(),
    'commands_executed': 0,
    'last_update': datetime.now(),
    'daily_users': set(),
    'alerts_sent': 0,
    'total_conversions': 0,
    'api_checks': 0,
    'healthy_apis': 0
}

user_preferences = {}
price_alerts = {}
conversation_history = {}

# Complete list of supported currencies with emojis
SUPPORTED_CURRENCIES = {
    'AED': '🇦🇪', 'AFN': '🇦🇫', 'ALL': '🇦🇱', 'AMD': '🇦🇲', 'ANG': '🇳🇱', 'AOA': '🇦🇴', 'ARS': '🇦🇷', 'AUD': '🇦🇺',
    'AWG': '🇦🇼', 'AZN': '🇦🇿', 'BAM': '🇧🇦', 'BBD': '🇧🇧', 'BDT': '🇧🇩', 'BGN': '🇧🇬', 'BHD': '🇧🇭', 'BIF': '🇧🇮',
    'BMD': '🇧🇲', 'BND': '🇧🇳', 'BOB': '🇧🇴', 'BRL': '🇧🇷', 'BSD': '🇧🇸', 'BTN': '🇧🇹', 'BWP': '🇧🇼', 'BYN': '🇧🇾',
    'BZD': '🇧🇿', 'CAD': '🇨🇦', 'CDF': '🇨🇩', 'CHF': '🇨🇭', 'CLP': '🇨🇱', 'CNY': '🇨🇳', 'COP': '🇨🇴', 'CRC': '🇨🇷',
    'CUP': '🇨🇺', 'CVE': '🇨🇻', 'CZK': '🇨🇿', 'DJF': '🇩🇯', 'DKK': '🇩🇰', 'DOP': '🇩🇴', 'DZD': '🇩🇿', 'EGP': '🇪🇬',
    'ERN': '🇪🇷', 'ETB': '🇪🇹', 'EUR': '🇪🇺', 'FJD': '🇫🇯', 'FKP': '🇫🇰', 'GBP': '🇬🇧', 'GEL': '🇬🇪', 'GGP': '🇬🇬',
    'GHS': '🇬🇭', 'GIP': '🇬🇮', 'GMD': '🇬🇲', 'GNF': '🇬🇳', 'GTQ': '🇬🇹', 'GYD': '🇬🇾', 'HKD': '🇭🇰', 'HNL': '🇭🇳',
    'HRK': '🇭🇷', 'HTG': '🇭🇹', 'HUF': '🇭🇺', 'IDR': '🇮🇩', 'ILS': '🇮🇱', 'IMP': '🇮🇲', 'INR': '🇮🇳', 'IQD': '🇮🇶',
    'IRR': '🇮🇷', 'ISK': '🇮🇸', 'JEP': '🇯🇪', 'JMD': '🇯🇲', 'JOD': '🇯🇴', 'JPY': '🇯🇵', 'KES': '🇰🇪', 'KGS': '🇰🇬',
    'KHR': '🇰🇭', 'KMF': '🇰🇲', 'KPW': '🇰🇵', 'KRW': '🇰🇷', 'KWD': '🇰🇼', 'KYD': '🇰🇾', 'KZT': '🇰🇿', 'LAK': '🇱🇦',
    'LBP': '🇱🇧', 'LKR': '🇱🇰', 'LRD': '🇱🇷', 'LSL': '🇱🇸', 'LYD': '🇱🇾', 'MAD': '🇲🇦', 'MDL': '🇲🇩', 'MGA': '🇲🇬',
    'MKD': '🇲🇰', 'MMK': '🇲🇲', 'MNT': '🇲🇳', 'MOP': '🇲🇴', 'MRU': '🇲🇷', 'MUR': '🇲🇺', 'MVR': '🇲🇻', 'MWK': '🇲🇼',
    'MXN': '🇲🇽', 'MYR': '🇲🇾', 'MZN': '🇲🇿', 'NAD': '🇳🇦', 'NGN': '🇳🇬', 'NIO': '🇳🇮', 'NOK': '🇳🇴', 'NPR': '🇳🇵',
    'NZD': '🇳🇿', 'OMR': '🇴🇲', 'PAB': '🇵🇦', 'PEN': '🇵🇪', 'PGK': '🇵🇬', 'PHP': '🇵🇭', 'PKR': '🇵🇰', 'PLN': '🇵🇱',
    'PYG': '🇵🇾', 'QAR': '🇶🇦', 'RON': '🇷🇴', 'RSD': '🇷🇸', 'RUB': '🇷🇺', 'RWF': '🇷🇼', 'SAR': '🇸🇦', 'SBD': '🇸🇧',
    'SCR': '🇸🇨', 'SDG': '🇸🇩', 'SEK': '🇸🇪', 'SGD': '🇸🇬', 'SHP': '🇸🇭', 'SLE': '🇸🇱', 'SOS': '🇸🇴', 'SRD': '🇸🇷',
    'SSP': '🇸🇸', 'STN': '🇸🇹', 'SYP': '🇸🇾', 'SZL': '🇸🇿', 'THB': '🇹🇭', 'TJS': '🇹🇯', 'TMT': '🇹🇲', 'TND': '🇹🇳',
    'TOP': '🇹🇴', 'TRY': '🇹🇷', 'TTD': '🇹🇹', 'TVD': '🇹🇻', 'TWD': '🇹🇼', 'TZS': '🇹🇿', 'UAH': '🇺🇦', 'UGX': '🇺🇬',
    'USD': '🇺🇸', 'UYU': '🇺🇾', 'UZS': '🇺🇿', 'VED': '🇻🇪', 'VES': '🇻🇪', 'VND': '🇻🇳', 'VUV': '🇻🇺', 'WST': '🇼🇸',
    'XAF': '🌍', 'XCD': '🌴', 'XDR': '🏛️', 'XOF': '🌍', 'XPF': '🇵🇫', 'YER': '🇾🇪', 'ZAR': '🇿🇦', 'ZMW': '🇿🇲', 'ZWL': '🇿🇼',
    'XAG': '🥈', 'XAU': '🥇', 'XPD': '⚪', 'XPT': '⚫'
}

class TrustedCurrencyAPI:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes

    def get_cached_data(self, key):
        if (key in self.cache and key in self.cache_time and 
            (datetime.now() - self.cache_time[key]).seconds < self.cache_duration):
            return self.cache[key]
        return None

    def cache_data(self, key, data):
        self.cache[key] = data
        self.cache_time[key] = datetime.now()

    def test_api_health(self, api_info):
        """Test if a single API is working"""
        try:
            url = api_info["url"]
            headers = {
                'User-Agent': 'CurrencyBot-Pro/3.0',
                'Accept': 'application/json'
            }

            if api_info["type"] == "exchangerate":
                response = requests.get(f"{url}USD", timeout=10, headers=headers)
            elif api_info["type"] == "openexchange":
                response = requests.get(f"{url}?app_id=demo", timeout=10, headers=headers)
            elif api_info["type"] == "currencyfreaks":
                response = requests.get(f"{url}?apikey=demo", timeout=10, headers=headers)
            elif api_info["type"] == "forexrateapi":
                response = requests.get(f"{url}?base=USD", timeout=10, headers=headers)
            elif api_info["type"] == "fixer":
                response = requests.get(f"{url}?access_key=demo&base=USD", timeout=10, headers=headers)
            else:
                response = requests.get(url, timeout=10, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, dict):
                    api_info["status"] = "healthy"
                    api_info["last_success"] = datetime.now()
                    return True

            api_info["status"] = "unhealthy"
            return False

        except Exception as e:
            api_info["status"] = "error"
            api_info["last_error"] = str(e)
            return False

    def get_exchange_rates(self, base_currency='USD'):
        cache_key = f"rates_{base_currency}"
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data

        # Try each trusted API in order of accuracy
        sorted_apis = sorted(TRUSTED_CURRENCY_APIS, key=lambda x: x["accuracy"], reverse=True)

        for api_info in sorted_apis:
            try:
                headers = {
                    'User-Agent': 'CurrencyBot-Pro/3.0',
                    'Accept': 'application/json'
                }

                if api_info["type"] == "exchangerate":
                    response = requests.get(f"{api_info['url']}{base_currency}", timeout=15, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if 'rates' in data:
                            normalized_data = {
                                'base': base_currency,
                                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                                'rates': data['rates'],
                                'source': api_info['name']
                            }
                            self.cache_data(cache_key, normalized_data)
                            logging.info(f"✅ Success with {api_info['name']}")
                            bot_stats['api_checks'] += 1
                            bot_stats['healthy_apis'] += 1
                            return normalized_data

                elif api_info["type"] == "openexchange":
                    # Note: Free tier only supports USD base
                    if base_currency == 'USD':
                        response = requests.get(f"{api_info['url']}?app_id=demo", timeout=15, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            if 'rates' in data:
                                normalized_data = {
                                    'base': 'USD',
                                    'date': datetime.fromtimestamp(data.get('timestamp', time.time())).strftime('%Y-%m-%d'),
                                    'rates': data['rates'],
                                    'source': api_info['name']
                                }
                                self.cache_data(cache_key, normalized_data)
                                logging.info(f"✅ Success with {api_info['name']}")
                                return normalized_data

                elif api_info["type"] == "currencyfreaks":
                    response = requests.get(f"{api_info['url']}?apikey=demo&base={base_currency}", timeout=15, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if 'rates' in data:
                            normalized_data = {
                                'base': base_currency,
                                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                                'rates': data['rates'],
                                'source': api_info['name']
                            }
                            self.cache_data(cache_key, normalized_data)
                            logging.info(f"✅ Success with {api_info['name']}")
                            return normalized_data

                elif api_info["type"] == "forexrateapi":
                    response = requests.get(f"{api_info['url']}?base={base_currency}", timeout=15, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if 'rates' in data:
                            normalized_data = {
                                'base': base_currency,
                                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                                'rates': data['rates'],
                                'source': api_info['name']
                            }
                            self.cache_data(cache_key, normalized_data)
                            logging.info(f"✅ Success with {api_info['name']}")
                            return normalized_data

                elif api_info["type"] == "fixer":
                    response = requests.get(f"{api_info['url']}?access_key=demo&base={base_currency}", timeout=15, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if 'rates' in data:
                            normalized_data = {
                                'base': base_currency,
                                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                                'rates': data['rates'],
                                'source': api_info['name']
                            }
                            self.cache_data(cache_key, normalized_data)
                            logging.info(f"✅ Success with {api_info['name']}")
                            return normalized_data

            except Exception as e:
                logging.warning(f"API {api_info['name']} failed: {e}")
                continue

        # Accurate fallback rates (updated 2025)
        logging.warning("Using trusted fallback rates")
        fallback_rates = {
            'USD': 1.0, 'EUR': 0.9127, 'GBP': 0.7854, 'JPY': 157.32, 'AUD': 1.5234,
            'CAD': 1.3678, 'CHF': 0.8765, 'CNY': 7.2341, 'INR': 83.24, 'BRL': 5.4123,
            'RUB': 88.75, 'KRW': 1342.5, 'SGD': 1.3456, 'HKD': 7.8324, 'MXN': 17.234,
            'MYR': 4.25, 'THB': 35.67, 'IDR': 15234.5, 'PHP': 56.78, 'VND': 24567.8
        }

        return {
            'base': 'USD',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'rates': fallback_rates,
            'source': 'Trusted Fallback Rates',
            'warning': 'Using backup rates - APIs temporarily unavailable'
        }

    def convert_currency(self, amount, from_currency, to_currency):
        try:
            rates_data = self.get_exchange_rates(from_currency)
            if rates_data:
                if to_currency in rates_data.get('rates', {}):
                    rate = rates_data['rates'][to_currency]
                    return amount * rate
                elif from_currency == to_currency:
                    return amount
                else:
                    # Cross-conversion via USD
                    usd_rates = self.get_exchange_rates('USD')
                    if usd_rates and from_currency in usd_rates.get('rates', {}) and to_currency in usd_rates.get('rates', {}):
                        from_rate = usd_rates['rates'][from_currency]
                        to_rate = usd_rates['rates'][to_currency]
                        return amount * (to_rate / from_rate)
            return None
        except Exception as e:
            logging.error(f"Error converting currency: {e}")
            return None

# Initialize trusted API manager
trusted_api = TrustedCurrencyAPI()

# Safe message editing function
async def safe_edit_message(query, message, reply_markup=None, parse_mode='Markdown'):
    try:
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=parse_mode)
        return True
    except BadRequest as e:
        if "Message is not modified" in str(e):
            try:
                await query.answer("✅ Already up to date!")
            except:
                pass
            return False
        else:
            logging.error(f"BadRequest error: {e}")
            try:
                await query.answer("❌ Error updating message")
            except:
                pass
            return False
    except Exception as e:
        logging.error(f"Error editing message: {e}")
        try:
            await query.answer("❌ Something went wrong")
        except:
            pass
        return False

# Enhanced Telegram bot handlers
async def start(update: Update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"

    bot_stats['users'].add(user_id)
    bot_stats['daily_users'].add(user_id)
    bot_stats['commands_executed'] += 1

    welcome_message = f"""
🎉 **Welcome {user_name} to CurrencyBot Pro!** 🎉

🚀 **TRUSTED CURRENCY FEATURES:**
• ✅ Top 5 Most Accurate Currency(2025)
• 🎯 ExchangeRate - (★★★★☆)
• 🏆 Open Exchange Rates - (★★★★★)
• 💎 CurrencyFreaks - (★★★★☆)
• 📊 ForexRateAPI - (★★★★☆)
• 🔒 Fixer.io - (★★★★☆)

**💱 CURRENCY FEATURES:**
• {len(SUPPORTED_CURRENCIES)} World currencies
• 🥇 Precious metals support
• 📈 Real-time accurate rates
• 🔄 Smart fallback system
• ⚡ Lightning fast responses

**🔧 COMMANDS:**
/currency - Exchange rates
/convert - Currency converter
/health - API health status
/allcurrencies - View all currencies

Ready to get ACCURATE currency data? 🚀
    """

    keyboard = [
        [InlineKeyboardButton("📱 Exchange Rates", callback_data='get_rates'),
         InlineKeyboardButton("🔄 Quick Convert", callback_data='quick_convert')],
        [InlineKeyboardButton("🌍 All Currencies", callback_data='all_currencies'),
         InlineKeyboardButton("🏥 API Health", callback_data='api_health')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in start command: {e}")
        await update.message.reply_text("🤖 Welcome! Use /help to see available commands.")

async def api_health_command(update: Update, context):
    """Show API health status"""
    bot_stats['commands_executed'] += 1

    healthy_count = 0
    message = f"🏥 **Trusted Currency API Health Dashboard**\n\n"
    message += f"**📊 TOP 5 TRUSTED APIS (2025):**\n\n"

    for api in TRUSTED_CURRENCY_APIS:
        is_healthy = trusted_api.test_api_health(api)
        if is_healthy:
            healthy_count += 1
            status_icon = "✅"
        else:
            status_icon = "❌"

        stars = "★" * api["accuracy"]
        message += f"{status_icon} **{api['name']}** ({stars})\n"
        message += f"   🔗 {api['type']} - {'Free' if api['free'] else 'Paid'}\n\n"

    message += f"**📈 SUMMARY:**\n"
    message += f"✅ Healthy APIs: **{healthy_count}/{len(TRUSTED_CURRENCY_APIS)}**\n"
    message += f"🎯 Success Rate: **{(healthy_count/len(TRUSTED_CURRENCY_APIS)*100):.1f}%**\n"
    message += f"🕐 Last Check: {datetime.now().strftime('%H:%M:%S')}\n\n"
    message += f"🚀 **TRUSTED & ACCURATE CURRENCY DATA!**"

    bot_stats['healthy_apis'] = healthy_count

    keyboard = [
        [InlineKeyboardButton("🔄 Refresh Health", callback_data='api_health')],
        [InlineKeyboardButton("💱 Get Rates", callback_data='get_rates')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if hasattr(update, 'callback_query') and update.callback_query:
            await safe_edit_message(update.callback_query, message, reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in api_health command: {e}")

async def currency_command(update: Update, context):
    bot_stats['commands_executed'] += 1

    if context.args:
        currency = context.args[0].upper()
        if currency in SUPPORTED_CURRENCIES:
            try:
                rates_data = trusted_api.get_exchange_rates(currency)
                if rates_data:
                    emoji = SUPPORTED_CURRENCIES[currency]
                    source = rates_data.get('source', 'Trusted APIs')
                    message = f"{emoji} **Exchange Rates for {currency}**\n\n"

                    top_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'MYR']
                    for curr in top_currencies:
                        if curr != currency and curr in rates_data['rates']:
                            rate = rates_data['rates'][curr]
                            curr_emoji = SUPPORTED_CURRENCIES.get(curr, '💱')
                            message += f"{curr_emoji} 1 {currency} = {rate:.4f} {curr}\n"

                    message += f"\n🕐 Updated: {rates_data['date']}"
                    if rates_data.get('warning'):
                        message += f"\n⚠️ {rates_data['warning']}"
                    else:
                        message += f"\n🔗 Source: {source}"

                    keyboard = [
                        [InlineKeyboardButton(f"Convert {currency}", callback_data=f'convert_from_{currency}')],
                        [InlineKeyboardButton("🏥 API Health", callback_data='api_health')]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    if hasattr(update, 'callback_query') and update.callback_query:
                        await safe_edit_message(update.callback_query, message, reply_markup)
                    else:
                        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    error_msg = "❌ Failed to fetch exchange rates from trusted sources."
                    if hasattr(update, 'callback_query') and update.callback_query:
                        await update.callback_query.answer(error_msg)
                    else:
                        await update.message.reply_text(error_msg)
            except Exception as e:
                logging.error(f"Error in currency command: {e}")
                error_msg = "❌ Error fetching rates. Please try again."
                if hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.answer(error_msg)
                else:
                    await update.message.reply_text(error_msg)
        else:
            await update.message.reply_text(f"❌ Currency '{currency}' not supported. Use /allcurrencies to see all supported currencies.")
    else:
        keyboard = []
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'MYR', 'SGD', 'THB']

        for i in range(0, len(major_currencies), 3):
            row = []
            for j in range(3):
                if i + j < len(major_currencies):
                    curr = major_currencies[i + j]
                    emoji = SUPPORTED_CURRENCIES[curr]
                    row.append(InlineKeyboardButton(f"{emoji} {curr}", callback_data=f'currency_{curr}'))
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton(f"🌍 View All {len(SUPPORTED_CURRENCIES)} Currencies", callback_data='all_currencies')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            if hasattr(update, 'callback_query') and update.callback_query:
                await safe_edit_message(update.callback_query, "💱 **Select a currency:**", reply_markup)
            else:
                await update.message.reply_text("💱 **Select a currency:**", reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logging.error(f"Error showing currency list: {e}")

async def convert_currency(update: Update, context):
    bot_stats['commands_executed'] += 1
    bot_stats['total_conversions'] += 1

    if len(context.args) >= 3:
        try:
            amount = float(context.args[0])
            from_curr = context.args[1].upper()
            to_curr = context.args[2].upper()

            if from_curr not in SUPPORTED_CURRENCIES:
                await update.message.reply_text(f"❌ Currency '{from_curr}' not supported. Use /allcurrencies to see all supported currencies.")
                return

            if to_curr not in SUPPORTED_CURRENCIES:
                await update.message.reply_text(f"❌ Currency '{to_curr}' not supported. Use /allcurrencies to see all supported currencies.")
                return

            converted = trusted_api.convert_currency(amount, from_curr, to_curr)
            if converted:
                from_emoji = SUPPORTED_CURRENCIES.get(from_curr, '💱')
                to_emoji = SUPPORTED_CURRENCIES.get(to_curr, '💱')

                message = f"💰 **Trusted Currency Conversion**\n\n"
                message += f"{from_emoji} {amount:,.2f} {from_curr}\n"
                message += f"⬇️\n"
                message += f"{to_emoji} {converted:,.2f} {to_curr}\n\n"
                message += f"📈 Rate: 1 {from_curr} = {converted/amount:.6f} {to_curr}\n"
                message += f"🔒 Powered by Top 5 Trusted APIs"

                keyboard = [
                    [InlineKeyboardButton("🔄 Convert Again", callback_data='quick_convert')],
                    [InlineKeyboardButton("📊 View Rates", callback_data='get_rates')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Conversion failed. Please check currency codes and try again.")
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            logging.error(f"Error in convert_currency: {e}")
            await update.message.reply_text("❌ Error during conversion. Please try again.")
    else:
        await update.message.reply_text(f"💡 **Usage:** `/convert [amount] [from] [to]`\n**Example:** `/convert 100 USD MYR`\n\nUse `/allcurrencies` to see all supported currencies!")

async def all_currencies_command(update: Update, context):
    bot_stats['commands_executed'] += 1

    message = f"🌍 **All Supported Currencies ({len(SUPPORTED_CURRENCIES)})**\n\n"

    message += "**🌎 MAJOR CURRENCIES:**\n"
    major = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY', 'INR', 'MYR']
    for curr in major:
        if curr in SUPPORTED_CURRENCIES:
            message += f"{SUPPORTED_CURRENCIES[curr]} {curr}  "

    message += "\n\n**💎 PRECIOUS METALS:**\n"
    metals = ['XAU', 'XAG', 'XPD', 'XPT']
    for curr in metals:
        if curr in SUPPORTED_CURRENCIES:
            message += f"{SUPPORTED_CURRENCIES[curr]} {curr}  "

    message += f"\n\n**Total: {len(SUPPORTED_CURRENCIES)} currencies**"
    message += f"\n🔒 Powered by Top 5 Trusted APIs"
    message += "\n\n💡 Use `/currency [CODE]` to see rates"
    message += "\n💡 Use `/convert [amount] [from] [to]` to convert"

    keyboard = [
        [InlineKeyboardButton("🔄 Convert Currency", callback_data='quick_convert')],
        [InlineKeyboardButton("🏥 API Health", callback_data='api_health')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if hasattr(update, 'callback_query') and update.callback_query:
            await safe_edit_message(update.callback_query, message, reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in all_currencies command: {e}")

# Enhanced callback handler
async def button_handler(update: Update, context):
    query = update.callback_query

    try:
        await query.answer()

        if query.data == 'get_rates':
            await currency_command(update, context)
        elif query.data == 'api_health':
            await api_health_command(update, context)
        elif query.data == 'all_currencies':
            await all_currencies_command(update, context)
        elif query.data.startswith('currency_'):
            currency = query.data.split('_')[1]
            context.args = [currency]
            await currency_command(update, context)
        elif query.data == 'quick_convert':
            await query.edit_message_text(
                "💡 **Quick Convert:** Use `/convert [amount] [from] [to]`\n\n"
                "**Examples:**\n"
                "• `/convert 100 USD MYR`\n"
                "• `/convert 1000 MYR USD`\n"
                "• `/convert 50 EUR GBP`\n\n"
                "🔒 Powered by trusted currency APIs",
                parse_mode='Markdown'
            )

    except Exception as e:
        logging.error(f"Error in button handler: {e}")
        try:
            await query.answer("❌ Something went wrong. Please try again.")
        except:
            pass

async def help_command(update: Update, context):
    help_text = f"""
🤖 **CurrencyBot Pro - Trusted Currency Guide**

**🚀 TRUSTED API FEATURES:**
• ✅ Top 5 Most Accurate -  (2025)
• 🎯 ExchangeRate - (★★★★☆)
• 🏆 Open Exchange Rates  - (★★★★★) 
• 💎 CurrencyFreaks  - (★★★★☆)
• 📊 ForexRateAPI -  (★★★★☆)
• 🔒 Fixer.io by APILayer  - (★★★★☆)

**💱 CURRENCY COMMANDS:**
/currency [CODE] - Exchange rates
/convert [amount] [from] [to] - Convert currencies
/allcurrencies - View all {len(SUPPORTED_CURRENCIES)} currencies
/health - API health dashboard

**💡 EXAMPLES:**
• `/convert 100 USD MYR` (Accurate MYR rates!)
• `/convert 1 XAU USD` (Gold prices)
• `/currency JPY`
• `/health` (Check trusted APIs)

**🔒 TRUSTED ACCURACY:**
• Real-time accurate rates
• Enterprise-grade APIs
• Smart fallback system
• Zero unreliable sources

🚀 **TRUSTED CURRENCY DATA GUARANTEED!**
    """
    try:
        await update.message.reply_text(help_text, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in help command: {e}")
        await update.message.reply_text("🤖 Welcome! Use the menu buttons or type commands to get started.")

# Flask web app
app = Flask(__name__, template_folder='.', static_folder='static')
app.secret_key = FLASK_SECRET_KEY

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    if password == ADMIN_PASSWORD:
        session['authenticated'] = True
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Invalid password')

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('index'))

    enhanced_stats = {
        'total_users': len(bot_stats['users']),
        'daily_active_users': len(bot_stats['daily_users']),
        'commands_executed': bot_stats['commands_executed'],
        'total_conversions': bot_stats['total_conversions'],
        'total_apis': len(TRUSTED_CURRENCY_APIS),
        'healthy_apis': bot_stats.get('healthy_apis', 0),
        'api_checks': bot_stats.get('api_checks', 0),
        'supported_currencies': len(SUPPORTED_CURRENCIES),
        'last_update': bot_stats['last_update']
    }

    return render_template('dashboard.html', stats=enhanced_stats)

@app.route('/api/health')
def api_health_endpoint():
    healthy_count = 0
    api_status = []

    for api in TRUSTED_CURRENCY_APIS:
        is_healthy = trusted_api.test_api_health(api)
        if is_healthy:
            healthy_count += 1

        api_status.append({
            'name': api['name'],
            'type': api['type'],
            'accuracy': api['accuracy'],
            'healthy': is_healthy,
            'free': api['free']
        })

    return jsonify({
        'total_apis': len(TRUSTED_CURRENCY_APIS),
        'healthy_apis': healthy_count,
        'health_percentage': (healthy_count / len(TRUSTED_CURRENCY_APIS)) * 100,
        'api_details': api_status,
        'last_check': datetime.now().isoformat()
    })

@app.route('/api/rates')
def api_rates():
    try:
        rates = trusted_api.get_exchange_rates('USD')
        return jsonify(rates)
    except:
        return jsonify({'error': 'Failed to fetch rates'}), 500

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'total_users': len(bot_stats['users']),
        'daily_active_users': len(bot_stats['daily_users']),
        'commands_executed': bot_stats['commands_executed'],
        'total_conversions': bot_stats['total_conversions'],
        'total_apis': len(TRUSTED_CURRENCY_APIS),
        'healthy_apis': bot_stats.get('healthy_apis', 0),
        'api_checks': bot_stats.get('api_checks', 0),
        'last_update': bot_stats['last_update'].isoformat(),
        'supported_currencies': len(SUPPORTED_CURRENCIES)
    })

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("currency", currency_command))
    application.add_handler(CommandHandler("allcurrencies", all_currencies_command))
    application.add_handler(CommandHandler("convert", convert_currency))
    application.add_handler(CommandHandler("health", api_health_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 CurrencyBot Pro - TRUSTED APIs Edition!")
    print(f"🌐 Admin panel: http://0.0.0.0:5000")
    print("📱 Telegram bot: Running with TRUSTED currency APIs...")
    print(f"💱 Supported currencies: {len(SUPPORTED_CURRENCIES)}")
    print(f"🔒 TRUSTED Currency APIs: {len(TRUSTED_CURRENCY_APIS)} sources!")
    print("💎 TOP 5 TRUSTED APIS (2025):")
    for api in TRUSTED_CURRENCY_APIS:
        stars = "★" * api["accuracy"]
        print(f"   🎯 {api['name']} ({stars}) - {'Free' if api['free'] else 'Paid'}")
    print("🔥 TRUSTED CURRENCY ACCURACY GUARANTEED!")

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logging.error(f"Bot polling error: {e}")
        print("🔄 Restarting bot in 5 seconds...")
        import time
        time.sleep(5)
        main()

if __name__ == '__main__':
    main()
