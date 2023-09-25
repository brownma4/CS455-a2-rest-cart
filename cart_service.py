import os
import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'carts.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(10), default="4.99")
    quantity = db.Column(db.Integer, default=1) 
    user_id = db.Column(db.Integer, default=1) 

# Endpoint 1: returns the cart of the specified user
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):

    # queries the products in the database to see if the item is already in the cart
    cart_products = Product.query.filter_by(user_id=user_id).all()

    # stores the total price of the cart
    total_price = 0

    # list to store the products in this user's cart
    user_products = []

    # Iterate over the list of products and access the attributes directly
    for product in cart_products:

        # gets the user's products
        if product.user_id == user_id:
            user_products.append(product)
            total_price += product.quantity * float(product.price)

    # cuts the price off to 2 decimal places
    price_string = float(f'{total_price:.2f}')
                         
    # returns the dict list of the user's products
    product_list = [{"id": product.id, "name": product.name, "price": product.price, "quantity": product.quantity, "user_id": product.user_id} for product in user_products]
    return jsonify({"products": product_list, "price": price_string}), 200
    

# Endpoint 2: Adds a product to a cart, and removes it from the products server
@app.route("/cart/<int:user_id>/add/<int:product_id>", methods=["POST"])
def add_product_to_cart(user_id, product_id):

    # connects to the products server to get all of the products
    response = requests.get('https://a-2-product-service.onrender.com/products')
    data = response.json()

    # gets the quantity
    info = request.json

    # parses the info for the product
    product_to_add = Product(**info)

    # gets the quantity (so we can change it to a negative value for the removal later)
    quantity = info["quantity"]

    # parses the available products
    products = data["products"]

    # checks to see if the product is on the server, and if it is, tries to add it to the cart
    for product in products:

        # if the item is avalable in the specified quantity, adds it to the cart
        if product["id"] == product_id:
            if product["quantity"] >= quantity:

                # need the name and price variables that we were missing before
                product_to_add.name = product["name"]
                product_to_add.price = product["price"]

                # creates a copy of the product with a negative quantity to remove it from the product server
                num_to_remove = -quantity
                product_to_remove = {"id": product_to_add.id, "name": product_to_add.name, "price": product_to_add.price, "quantity": num_to_remove, "user_id": 0}

                # product to add to the cart with the correct quantity and user_id
                add_to_cart = {"id": product["id"], "name": product["name"], "price": product["price"], "quantity": quantity, "user_id": user_id}
                
                # removes the amount of product that was added into the user's cart
                response = requests.post('https://a-2-product-service.onrender.com/products', json=product_to_remove)
                
                # the product to add to the cart
                add_to_cart2 = Product(**add_to_cart)

                # queries the products in the database to see if the item is already in the cart
                cart_products = Product.query.filter_by(user_id=user_id).all()

                # iterates through the products in the user's cart. If the product is already in it-
                # instead of creating another product, updates the quantity
                for product in cart_products:
                    if product.id == product_id:
                        product.quantity += quantity
                        db.session.commit()
                        return jsonify({"Cart product quantity updated": "yay"}), 200

                # if the product is not already in the cart, adds it to the cart
                db.session.add(add_to_cart2)
                db.session.commit()
                
                return jsonify({"message": "Product added to cart", "product": {"id": product_to_add.id, "name": product_to_add.name, "price": product_to_add.price, "quantity": product_to_add.quantity, "user_id": product_to_add.user_id}}), 201
         
    return jsonify({"error": "Product id not found"}), 404

# Endpoint 3: Adds a product to a cart, and removes it from the products server
@app.route("/cart/<int:user_id>/remove/<int:product_id>", methods=["POST"])
def remove_product_from_cart(user_id, product_id):
    info = request.json

    # parses the info for the product
    product_to_remove = Product(**info)

    # gets the quantity (so we can change it to a negative value for the removal later)
    quantity = info["quantity"]

    # queries the products in the database to see if the item is in the user's cart
    cart_products = Product.query.filter_by(user_id=user_id).all()

    # iterates through the products in the user's cart to see if the user has it
    for product in cart_products:
        if product.id == product_id:
            if product.quantity >= quantity:

                # product to remove from the cart with the correct quantity and price
                remove_from_cart = {"id": product_id, "name": product.name, "price": product.price, "quantity": quantity, "user_id": user_id}

                # adds the amount of product that was removed from the cart back into the available products server
                requests.post('https://a-2-product-service.onrender.com/products', json=remove_from_cart)

                product.quantity = product.quantity - quantity

                if product.quantity == 0:
                    db.session.delete(product)
                    db.session.commit()
                    return jsonify({"Product removed from cart": "yay"}), 200

            else:
                return jsonify({"error": "Quantity of products to remove from cart too high"}), 404
            

            db.session.commit()
            return jsonify({"Cart product quantity updated": "yay"}), 200
         
    return jsonify({"error": "Product not in cart"}), 404


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=10000)
