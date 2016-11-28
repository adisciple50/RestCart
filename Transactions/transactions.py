from .objects import Order

from money import Money
# Currency Conversion Handling
# https://pypi.python.org/pypi/money/1.3.0

import json
import random

import paypalrestsdk
paypalrestsdk.configure(json.loads('settings.json')['paypal'])

class Transaction:
        def __init__(self,user:str,password:str,order:Order,currency_symbol='GBP'):
            self.money = order.total
            self.status = "Started"
            self.status_code = 0
            self.order = Order
            self.transaction_id = random.randint(0,100000000000000000000000000000000000)
            self.payment = ""
            self.total = Money()

        def open_invoice(self):
            self.status = "Invoice Open"
            self.status_code = 1
            start_transaction_url = {'transaction_url':'url'}
            return start_transaction_url
        def process_payment(self):
            self.payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": "http://localhost:3000/process",
                    "cancel_url": "http://localhost:3000/cancel"
                },
            "transactions": [{
                "item_list": self.order.to_paypal_transaction_items_list(),
                "amount": {
                    "total": str(self.order.total),
                    "currency": "GBP"},
                "description": "Payment To GlueDot Candles"}]})

            if self.payment.create():
                print("Payment created successfully")
                for link in self.payment.links:
                    if link.method == "REDIRECT":
                        # Capture redirect url
                        redirect_url = str(link.href) #send this link to the front end
            else:
                print(self.payment.error)

            self.status_code = 2
            self.status = "Processing Payment"
            return (redirect_url)
        def confirm_payment(self):
            self.status_code = 3
            if self.payment.execute({"payer_id": self.payment.id}):
                self.status = "Payment Succesful"
                print("Payment[%s] execute successfully" % (self.payment.id))
                self.status_code = 6
            else:
                print(self.payment.error)
                self.status = "Payment Unsuccesful"
                self.status_code = 4
        def close_invoice(self):
            if self.status == "Payment Succesful":
                self.status_code = 7
                self.status = "Invoice Paid"
            elif self.status == "Payment Unsuccesful":
                self.status_code = 5
                self.status = "Invoice Canceled"
            return self.status
        def __int__(self):
            return int(self.status_code)
