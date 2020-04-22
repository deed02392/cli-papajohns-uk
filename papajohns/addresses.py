from papajohns.api import Api

class Addresses:
    def __init__(self, postcode):
        self.postcode = postcode

    def get_addresses_from_postcode(self):
        ...