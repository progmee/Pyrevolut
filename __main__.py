from pyrevolut import Client


from iso4217 import Currency

import webbrowser

client = Client("sk_yptAts8q-cM63fbPgt6QghRqXuyoN_xuy0fgHDdPAe81Bg36G63ys4Z4LMjWugOY", sandbox=True)
#order : Client.Order = client.create_order(50, Currency.EUR, "https://google.com")

#webhooks = client.retrieve_webhooks()
#print(len(webhooks)) # Webhooks amount

#webhooks[0].delete()

#print(webhooks[0].url, webhooks[0].events)

# Open in webbroser a url
#webbrowser.open(order.retrieve()['checkout_url'])