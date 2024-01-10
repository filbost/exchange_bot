import telebot
import requests

class APIException(Exception):
    pass

class CurrencyConverter:
    @staticmethod
    def get_exchange_rate(base_currency, target_currency):
        # В данном примере используется Open Exchange Rates API поэтому вся валюта на английском : RUB, USD, EUR, TRY, CNY
        api_key = '2b8b64466e80b69ed5b22099'
        url = f'https://open.er-api.com/v6/latest/{base_currency}?apikey={api_key}'

        response = requests.get(url)
        data = response.json()

        if 'error' in data:
            raise APIException(f'Ошибка при получении курса валют: {data["error"]["description"]}')

        rates = data['rates']
        if target_currency not in rates:
            raise APIException(f'Неверная валюта: {target_currency}')

        return rates[target_currency]

class CurrencyConverterBot:
    def __init__(self, token):
        self.token = token
        self.bot = telebot.TeleBot(token)
        self.converter = CurrencyConverter()

    def start_bot(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, "Hello! This bot converts currency. Just send a message in the following format:\n"
                                    "<currency name1> <currency name2> <currency amount>")

        @self.bot.message_handler(func=lambda message: True)
        def convert_currency(message):
            try:
                input_text = message.text.split()
                if len(input_text) != 3:
                    raise APIException('Wrong format. Enter: <currency1> <currency2> <amount of currency1>')

                base_currency, target_currency, amount = input_text
                amount = float(amount)

                exchange_rate = self.converter.get_exchange_rate(base_currency, target_currency)
                converted_amount = amount * exchange_rate

                result_message = f'{amount} {base_currency} = {converted_amount:.2f} {target_currency}'
                self.bot.reply_to(message, result_message)

            except APIException as e:
                self.bot.reply_to(message, f'Ошибка: {str(e)}')

        self.bot.polling(none_stop=True)

if __name__ == "__main__":
    from config import TELEGRAM_BOT_TOKEN

    bot = CurrencyConverterBot(TELEGRAM_BOT_TOKEN)
    bot.start_bot()
