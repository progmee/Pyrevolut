import hmac, hashlib

def is_valide_webhook(secret : str, body : bytes, signature : str) -> bool:
    """
    Validate the signature of an incoming webhook request using HMAC.

    This function ensures that the webhook request is genuinely sent by
    the provider and has not been tampered with. It computes the HMAC
    of the request body using the shared secret and compares it to the
    signature provided in the request headers.

    Attributes:
        body (bytes): The raw HTTP request body as bytes.
        signature (str): The signature string sent in the webhook headers.
        secret (str): The shared secret key used for HMAC computation.
    """

    hmac_hash : hmac = hmac.new(secret, body, hashlib.sha256) # Compute hmac hash

    return hmac_hash.compare_digest(signature)