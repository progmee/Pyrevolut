class RevolutAPIException(Exception):
    """
    Custom exception to handle errors returned by the Revolut API.

    Attributes:
        status_code (int): HTTP status code returned by the API.
        message (str): Error message returned by the API.
    """

    def __init__(self, status_code : int, message : str):
        super().__init__(f"Revolut API error {status_code}. {message}.")