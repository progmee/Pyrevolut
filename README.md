# Revolut Merchant API Python Client

A lightweight Python library to interact with the [Revolut Merchant API](https://developer.revolut.com/docs/merchant/pay-order).  
It allows you to create, retrieve, and cancel orders, handle currencies correctly, and work in both sandbox and production environments.

---

## Features

- **Client class**: Manage authentication and API requests.  
- **Order class**: Create, retrieve, and cancel orders.  
- **Currency support**: Uses `iso4217.Currency` for accurate minor unit conversion.  
- **Error handling**: Custom exceptions (`RevolutAPIException`) for failed requests.  
- **Sandbox & Production**: Easy switching between environments.  

---

## Installation

```bash
pip install iso4217 requests
