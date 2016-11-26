from decimal import Decimal
from money import Money, xrates

xrates.install('money.exchange.SimpleBackend')



# use google datastore to pickle an order!
class Order:
    def __init__(self,currency_code:str='GBP'):
        self.order_dict = {}
        self.total = Money(amount=0,currency=currency_code)

    def from_dict(self,item_cost_pairs:dict):
        self.order_dict.update(item_cost_pairs)


        return self.order_dict

    def from_tuple_list(self,item_price_pairs:dict):
        order_dict = {}
        for line in item_price_pairs:
            order_dict.update({str(line[0]):str(line[1])})
            self.total.amount += Decimal(line[1])
        self.order_dict.update(order_dict)
        return self.order_dict

    def total_to_gbp(self):
        return self.total.to('GBP')

    def total_to_currency(self,new_currency_code:str):
        return self.total.to(new_currency_code)

    def add_line(self,item:str,cost:str,quantity:int=1):
        for line in range(quantity):
            self.order_dict.update({str(item):str(cost)})
        return self.order_dict



