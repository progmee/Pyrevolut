# Pyrevolut

A lightweight Python library to interact with the Revolut Merchant API.

This library provides a simple and intuitive interface to manage orders, handle currencies, and operate seamlessly in both sandbox and production environments.

---

## Features

- **Client Class**: Manages authentication and API requests.
- **Order Class**: Facilitates creating, retrieving, and canceling orders.
- **Currency Support**: Utilizes `iso4217.Currency` for accurate minor unit conversion.
- **Error Handling**: Custom exceptions (`RevolutAPIException`) for failed requests.
- **Environment Support**: Easily switch between sandbox and production environments.

---

## Installation

Install via pip:

```bash
pip install pyrevolut
