from enum import Enum


class ServiceTicketNames(Enum):
    ACCESS_TICKET = ("AccessTicket", "ticket")
    CSRF_TOKEN = ("CSRFToken", "CSRFPreventionToken")

    def __init__(self, keyring_name: str, response_field: str) -> None:
        self.keyring_name: str = keyring_name
        self.response_field: str = response_field


class ServiceNames:
    TOKEN_SERVICE = "PrivvyCeeToken"
    CONFIG_SERVICE = "PrivvyCeeTui"
    
    # API Key username 
    API_KEY_USERNAME = "PVE_API_Key"
