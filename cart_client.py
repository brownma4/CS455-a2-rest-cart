import os
import requests
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'carts.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# returns the cart of the specified user_id
def get_cart(user_id):
    response = requests.get(f'http://127.0.0.1:5001/cart/{user_id}')
    data = response.json()
    return data

# adds a product to the cart
def add_product(user_id, product_id, quantity):

    # makes a dict to send (note: missing the name and price, it will be fixed later)
    info = {
        "id": product_id,
        "name": "null",
        "price": "null",
        "quantity": quantity,
        "user_id": user_id
    }

    response = requests.post(f'http://127.0.0.1:5001/cart/{user_id}/add/{product_id}', json=info)
    data = response.json()
    return data

# removes a product from the cart 
def remove_product(user_id, product_id, quantity):

    # makes a  product out of the data
    info = {
        "id": product_id,
        "name": "null",
        "price": "null",
        "quantity": quantity,
        "user_id": user_id
    }

    response = requests.post(f'http://127.0.0.1:5001/cart/{user_id}/remove/{product_id}', json=info)
    data = response.json()
    return data

if __name__ == '__main__':

    #tests

    cart = get_cart(2)
    print(f"\nCart for user 2:")
    print(cart)

    print(f"\nAdding strawberries to user 2's cart")
    add_strawberries = add_product(2, 1, 0)
    print(add_strawberries)
    
    print(f"\nCart for user 2:")
    print(get_cart(2))

    print(f"\Removing strawberries from user 2's cart")
    print(remove_product(2, 1, 3))
    
    print(f"\nCart for user 2:")
    print(get_cart(2))
