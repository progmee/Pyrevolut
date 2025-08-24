from pyrevolut import Client, Order
from iso4217 import Currency

import webbrowser

client = Client("your_secret_sandbox_key", sandbox=True)
order : Order = client.create_order(50, Currency.EUR, "https://google.com")

# Open in webbroser a url
webbrowser.open(order.retrieve()['checkout_url'])