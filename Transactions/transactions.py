# from importlib._bootstrap_external import _check_name

from Transactions.objects import Order

from money import Money
# Currency Conversion Handling
# https://pypi.python.org/pypi/money/1.3.0

import json
import random

import paypalrestsdk

settings_file = open('../settings.json')
settings = settings_file.read()

settings_json = json.loads(settings)

paypalrestsdk.configure(settings_json["paypal"])

class Transaction:
        def __init__(self,user:str,password:str,order:Order,currency_symbol='GBP'):
            self.money = order.__money__()
            self.status = "Started"
            self.status_code = 0
            self.order = order
            self.transaction_id = random.randint(0,100000000000000000000000000000000000)
            self.payment = ""
            self.total = order.total.amount

        def open_invoice(self):
            self.status = "Invoice Open"
            self.status_code = 1
            redirect_URLS = {"return_url": "http://localhost:3000/process","cancel_url": "http://localhost:3000/cancel"}
            return redirect_URLS
            # TODO
        def process_payment(self):
            print("order total: ",self.order.total.amount)
            print("paypal order is: ",self.order.to_paypal_transaction_items_list())
            self.payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": self.open_invoice(),
            "transactions": [{
                "item_list": self.order.to_paypal_transaction_items_list(),
                "amount": {
                    "total": str(self.total),
                    "currency": "GBP"
                },
                "description": "Payment To GlueDot Candles"
                }]
            })

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

if __name__ == "__main__":
    # from .objects import Order
    o = Order(currency_code="GBP")
    o.add_to_folder_from_dict({"wax": {"price":"10.00","quantity":3}, "Candles": {"price":"10.00","quantity":2}}) # second dildo overrides first dildo, counting doesnt work!
    t = Transaction("deddokatana","Bananadine777",o)
    print(t.process_payment())