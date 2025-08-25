import requests

from iso4217 import Currency
from decimal import Decimal
from typing import Union
from enum import Enum

REVOLUT_PRODUCTION_URL : str = "https://merchant.revolut.com" # Production URL to send requests.
REVOLUT_SANDBOX_URL : str = "https://sandbox-merchant.revolut.com" # Sandbox URL to send requests within dedicated env.

REVOLUT_API_VERSION : str = "2024-09-01" # The version of the Merchant API, specified in YYYY-MM-DD format.

class RevolutAPIException(Exception):
    """
    Custom exception to handle errors returned by the Revolut API.

    Attributes:
        status_code (int): HTTP status code returned by the API.
        message (str): Error message returned by the API.
    """

    def __init__(self, status_code : int, message : str):
        super().__init__(f"Revolut API error {status_code}. {message}.")

class Client():
    """
    Represents a Revolut Merchant API client for communicating with the server.

    Attributes:
        url (str): Base URL of the Revolut API (sandbox or production).
        POST_HEADERS (dict): Headers used for POST requests.
        GET_HEADERS (dict): Headers used for GET requests.
    """

    class Order():
        """
        Represents a Revolut order and provides operations on it.

        Attributes:
            client (Client): The Revolut Client instance that created this order.
            id (str): The unique identifier of the order.
        """

        def __init__(self, client : "Client", data : dict) -> "Client":
            """
            Initializes an Order object with data returned from the API.

            Args:
                client (Client): The Revolut Client instance.
                data (dict): JSON response from Revolut API containing order data.
            """

            self.client = client
            self.id = data['id']

        def retrieve(self) -> dict:
            """
            Fetches the latest data for this order from the Revolut API.

            Returns:
                dict: The order data returned by the API.
            """

            data = self.client._request("GET", f'/api/orders/{self.id}', headers=self.client.GET_HEADERS)
            return data
        
        def cancel(self) -> bool:
            """
            Cancels this order if it is in 'pending' state.

            Returns:
                bool: True if the order was successfully canceled, False otherwise.
            """

            # Retrieve data from order 
            data : dict = self.retrieve()
            state : str = data.get('state') # Get order state

            # Check that current state can be canceled
            if state == 'pending':
                # Cancel order
                self.client._request("POST", f'/api/orders/{self.id}/cancel', headers=self.client.POST_HEADERS)

                return True
            return False

    class Webhook:
        """
        Represents a Revolut webhook and provides methods to manage it.

        Attributes:
            id (str): Unique identifier of the webhook.
            url (str): Endpoint URL where Revolut sends webhook events.
            events (list[str]): List of events the webhook listens to.
            signing_secret (str): Secret key to verify webhook payload authenticity.
            client (Client): Reference to the Revolut Client instance.
        """

        class Events(Enum):
            """
            Enum representing all possible webhook events for orders.
            """
            ORDER_COMPLETED = 'ORDER_COMPLETED'      # Order fully completed
            ORDER_AUTHORISED = 'ORDER_AUTHORISED'    # Order authorized but not yet captured
            ORDER_CANCELED = 'ORDER_CANCELED'        # Order canceled
        
        def __init__(self, client: "Client", data: dict):
            """
            Initialize a Webhook object with data from the Revolut API.

            Args:
                client (Client): The Revolut API client that created or retrieved this webhook.
                data (dict): Dictionary containing webhook data from the API.
            """
            self.id = data.get('id')
            self.url = data.get('url')
            self.events = data.get('events')
            self.signing_secret = data.get('signing_secret')
            self.client = client

        def delete(self):
            """
            Delete this webhook from the Revolut API.

            Sends a DELETE request to remove the webhook permanently.
            """
            self.client._request(
                "DELETE",
                f'/api/1.0/webhooks/{self.id}',
                headers=self.client.POST_HEADERS  # Use POST_HEADERS to include proper authorization and content-type
            )

        def update(self, url: str):
            """
            Update the webhook's URL and/or events.

            Sends a PUT request to the Revolut API to modify the webhook.

            Args:
                url (str, optional): New URL for the webhook.
            """

            payload : dict = {
                'url': url,
                'events': self.events
            }

            # Send PUT request to update webhook
            self.client._request(
                "PUT",
                f'/api/1.0/webhooks/{self.id}',
                headers=self.client.POST_HEADERS,  # Use proper headers including content-type
                json=payload
            )

    def __init__(self, secret_key : str, sandbox : bool = False):
        AUTHORIZATION = 'Authorization' # Authorization field

        self.url = REVOLUT_SANDBOX_URL if sandbox else REVOLUT_PRODUCTION_URL

        self.POST_HEADERS : dict = { # Post header pattern
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Revolut-Api-Version': REVOLUT_API_VERSION,
        AUTHORIZATION: f'Bearer {secret_key}'
        }

        self.DELETE_HEADERS : dict = {
            AUTHORIZATION : self.POST_HEADERS[AUTHORIZATION] 
        }

        self.GET_HEADERS = self.POST_HEADERS.copy() # Duplicate headers and remove content type field
        del self.GET_HEADERS['Content-Type'] # Remove key from get headers

    def _to_minor_units(self, amount : Decimal, currency : Currency) -> int:
        """
        Converts an amount from major currency units to minor units.

        Args:
            amount (Decimal): Amount in major units (e.g., 10.50 EUR).
            currency (Currency): ISO4217 Currency object.

        Returns:
            int: Amount in minor units (e.g., 1050 cents for 10.50 EUR).
        """

        # Decimals for currency
        multiplier = 10 ** currency.exponent

        return int(multiplier * amount)

    def _request(self, method : str, path : str, headers : str, json : dict = None) -> dict:
        """
        Sends a HTTP request to the Revolut API and handles response/errors.

        Args:
            method (str): HTTP method ('GET', 'POST', etc.).
            path (str): API endpoint path.
            headers (dict): Headers to include in the request.
            json (dict, optional): JSON payload for the request.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            RevolutAPIException: If the API returns an error status code.
            Exception: If JSON decoding fails.
        """

        url : str = self.url + path # Combine path and url

        # Send request to server
        response = requests.request(method, url, headers=headers, json=json)
        
        # Detect JSON decoding error
        try:
            data = response.json() # Get dict from response

        except requests.JSONDecodeError:
            raise Exception("Failed to decode JSON response.")

        # Notify about failed requests
        if response.status_code >= 400:
            message = data.get("message", "Unknown")

            raise RevolutAPIException(response.status_code, message)

        return data

    def retrieve_webhooks(self) -> list[Webhook]:
        """
        Retrieve all webhooks registered for the current Revolut account.

        Sends a GET request to the Revolut API and returns a list of Webhook objects.

        Returns:
            list[Webhook]: List of Webhook instances representing all registered webhooks.
        """
        # Send GET request to fetch all webhooks
        data = self._request('GET', '/api/1.0/webhooks', headers=self.GET_HEADERS)

        # Convert each webhook dictionary into a Webhook object
        webhooks: list[Client.Webhook] = [Client.Webhook(self, response) for response in data]

        return webhooks


    def create_webhook(self, url: str, events: list[Webhook.Events]) -> Webhook:
        """
        Create a new webhook for the current Revolut account.

        Sends a POST request to register a webhook with a URL and list of events.

        Args:
            url (str): The endpoint URL to receive webhook events.
            events (list[Webhook.Events]): List of webhook events to subscribe to.

        Returns:
            Webhook: The created Webhook object with its ID, signing secret, and subscribed events.

        Example:
            client.create_webhook(
                "https://example.com/webhook",
                [Client.Webhook.Events.ORDER_COMPLETED, Client.Webhook.Events.ORDER_AUTHORISED]
            )
        """
        # Prepare the payload for the API request
        payload: dict = {
            'url': url,
            'events': [event.value for event in events]  # Convert enum to string
        }

        # Send POST request to create the webhook
        data = self._request("POST", '/api/1.0/webhooks', headers=self.POST_HEADERS, json=payload)

        # Optionally print the response for debugging
        print(data)

        # Return a Webhook object representing the newly created webhook
        return Client.Webhook(self, data)


    def create_order(self, amount : Union[Decimal, int], currency : Currency, redirect_url : str):
        """
        Creates a new order in the Revolut API.

        Args:
            amount (Decimal|int): The order amount in major currency units.
            currency (Currency): ISO4217 Currency object.
            redirect_url (str): URL to redirect the customer after payment.

        Returns:
            Order: An Order object representing the created order.
        """
        
        # Create json format data
        payload = {
            'amount' : str(self._to_minor_units(amount, currency)),
            'currency' : currency.code,
            'redirect_url' : redirect_url
        }

        # Send POST request to create order
        data = self._request("POST", "/api/orders", headers=self.POST_HEADERS, json=payload)

        return Client.Order(self, data)
    
    def retrieve_orders(self) -> list[Order]:
        """
        Retrieves all orders from the Revolut API.

        Returns:
            list[Order]: A list of Order objects.
        """
        
        # Send POST request to create order
        data = self._request("GET", "/api/1.0/orders", headers=self.POST_HEADERS)
        orders : list[Client.Order] = [Client.Order(self, response) for response in data] # Orders list

        return orders