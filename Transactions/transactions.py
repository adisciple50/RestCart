# from importlib._bootstrap_external import _check_name

from Transactions.objects import Order

from money import Money
# Currency Conversion Handling
# https://pypi.python.org/pypi/money/1.3.0

import json
import random

import paypalrestsdk

# google datastore

from google.cloud import datastore as ds

dsc = ds.Client()

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
            self.ds_transaction_id = dsc.key("CheckoutTransaction") # this string is concatanated with the autoincrement - the keyfunction provisions a new key.
            self.ds_transaction = ds.Entity(key=self.ds_transaction_id)

        def open_invoice(self):
            self.status = "Invoice Open"
            self.status_code = 1
            redirect_URLS = {"return_url": "http://localhost:3000/process","cancel_url": "http://localhost:3000/cancel"}
            self.ds_transaction["status"] = self.status
            self.ds_transaction["status_code"] = self.status_code
            dsc.put(self.ds_transaction)
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
            self.status = "Creating Payment URL"
            self.ds_transaction["status"] = self.status
            dsc.put(self.ds_transaction)
            if self.payment.create():
                print("Payment created successfully")
                self.status = "Payment Created Successfully"
                self.ds_transaction["status"] = self.status
                dsc.put(self.ds_transaction)

                for link in self.payment.links:
                    if link.method == "REDIRECT":
                        # Capture redirect url
                        redirect_url = str(link.href) #send this link to the front end
            else:
                print(self.payment.error)

            self.status_code = 2
            self.ds_transaction["status_code"] = self.status_code
            self.status = "Payment URL Served"
            self.ds_transaction["status"] = self.status
            dsc.put(self.ds_transaction)
            return {"transaction_url":redirect_url,"transaction_id":str(self.ds_transaction.key.id)}

        def confirm_payment(self):
            self.status_code = 3
            self.ds_transaction["status_code"] = self.status_code
            if self.payment.execute({"payer_id": self.payment.id}):
                self.status = "Payment Successful"
                print("Payment[%s] execute successfully" % (self.payment.id))
                self.status_code = 6
                self.ds_transaction["status_code"] = self.status_code
                self.ds_transaction["status"] = self.status
                dsc.put(self.ds_transaction)
            else:
                print(self.payment.error)
                self.status = "Payment Unsuccesful"
                self.status_code = 4
                self.ds_transaction["status_code"] = self.status_code
                self.ds_transaction["status"] = self.status
                dsc.put(self.ds_transaction)
        def close_invoice(self):
            if self.status == "Payment Succesful":
                self.status_code = 7
                self.ds_transaction["status_code"] = self.status_code
                self.status = "Invoice Paid"
                self.ds_transaction["status"] = self.status
                dsc.put(self.ds_transaction)
            elif self.status == "Payment Unsuccesful":
                self.status_code = 5
                self.ds_transaction["status_code"] = self.status_code
                self.status = "Invoice Canceled"
                self.ds_transaction["status"] = self.status
                dsc.put(self.ds_transaction)
            return self.status
        def __int__(self):
            return int(self.status_code)

if __name__ == "__main__":
    # from .objects import Order
    o = Order(currency_code="GBP")
    o.add_to_order_from_dict({"Wax": {"price":"10.00","quantity":3}, "Candles": {"price":"10.00","quantity":2}}) # use this format when billing!
    t = Transaction("deddokatana","Bananadine777",o)
    print(t.process_payment())