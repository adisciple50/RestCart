from .types import Order

from money import Money
# Currency Conversion Handling
# https://pypi.python.org/pypi/money/1.3.0

import json

import paypalrestsdk
paypalrestsdk.configure(json.loads('settings.json')['paypal'])

class Transaction:
        def __init__(self,user:str,password:str,amount:str,order:Order,currency_symbol='GBP'):
            self.money = Money(amount=amount,currency=currency_symbol)
            self.status = "Started"
            self.status_code = 0
        def open_invoice(self):
            self.status = "Invoice Open"
            self.status_code = 1
            start_transaction_url = {'transaction_url':'url'}
            return start_transaction_url
        def process_payment(self):
            self.status_code = 2
            self.status = "Processing Payment"
            pass
        def confirm_payment(self):
            self.status_code = 3
            payment = ""
            if payment:
                self.status = "Payment Succesful"
                self.status_code = 6
            else:
                self.status = "Payment Unsuccesful"
                self.status_code = 4
        def close_invoice(self):
            if self.status == "Payment Succesful":
                self.status_code = 7
                self.status = "Invoice Paid"
            elif self.status == "Payment Unsuccesful":
                self.status_code = 5
                self.status = "Invoice Canceled"
        def __int__(self):
            return int(self.status_code)
