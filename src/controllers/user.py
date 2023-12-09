from flask import Blueprint, render_template, session, redirect, request,current_app, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import bcrypt
import math
import random


from src.utils import get_discount_price
usercontrol = Blueprint("user", __name__, template_folder="templates")

# List of quotes for Accessories of Bike
accessories_quotes = [
    "Explore the world with our premium bike accessories",
    "Enhance your ride with top-notch bike accessories",
    "Discover the perfect accessories for your bike"
]

# List of quotes for Bikes
bikes_quotes = [
    "Experience the thrill of speed with our top-quality bikes",
    "Ride in style with our premium selection of bikes",
    "Find your perfect bike for every adventure"
]



@usercontrol.route("/")
def dashboard():
    mongo = PyMongo(current_app)
    if 'email' in session:
        user = mongo.db.users.find_one({"email": session['email']})

        # Check if the user exists
        if user:
            # Get the name from the user's data
            name = user['name']
            selected_category = request.args.get('category')
            cart_items = user.get('cart', {})
            print("Cart items:", cart_items)
            total_quantity = calculate_total_cart_quantity(cart_items)
            # print("Total quantity in cart:", total_quantity)
            if selected_category is not None:
                selected_category = selected_category.lower()
                bike_products = mongo.db.products.find({"brand_name": selected_category})
            else:
                bike_products = mongo.db.products.find({"product_name": "bike"})
            return render_template('dashboard.html', name=name, bike_products=bike_products,total_quantity=total_quantity)
        else:
            return "User not found"
    else:
        return "Unauthorized access"
@usercontrol.route('/bikes')
def bikes():
    if 'email' not in session:
        return "Unauthorized access"

    mongo = PyMongo(current_app)
    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        return "User not found"
    
    name = user['name']
    random_quote = random.choice(bikes_quotes)
    selected_category = request.args.get('category')
    per_page = 6
    page = request.args.get('page', default=1, type=int)
    
    # Initialize total_products_count to a default value 
    total_products_count = 0

    if selected_category is not None:
        selected_category = selected_category.lower()
        total_products_count = mongo.db.products.count_documents({"brand_name": selected_category})
    
    # If category is None, set selected_category to None and query all products with "product_name": "bike"
    if selected_category is None:
        selected_category = None
        total_products_count = mongo.db.products.count_documents({"product_name": "bike"})
    
    # Calculate total_pages no matter which branch is taken
    total_pages = math.ceil(total_products_count / per_page)

    # Calculate the skip count to skip products on previous pages
    skip_count = (page - 1) * per_page

    if selected_category is not None:
        bike_products = mongo.db.products.find({"brand_name": selected_category}).skip(skip_count).limit(per_page)
    else:
        bike_products = mongo.db.products.find({"product_name": "bike"}).skip(skip_count).limit(per_page)
    _bike_products = [
        {
            "_id": bike_product.get("_id"),
            "product_name": bike_product.get("product_name"),
            "brand_name": bike_product.get("brand_name"),
            "model_name": bike_product.get("model_name"),
            "product_description": bike_product.get("product_description"),
            "price": bike_product.get("price"),
            "color": bike_product.get("color"),
            "warranty": bike_product.get("warranty"),
            "discount": bike_product.get("discount"),
            "photo_path": bike_product.get("photo_path"),
            'discounted_price': get_discount_price(float(bike_product.get("price")), float(bike_product.get("discount"))) 
            if float(bike_product.get("price"))!=get_discount_price(float(bike_product.get("price")), float(bike_product.get("discount"))) else None
        } for bike_product in bike_products
    ]
    cart_items = user.get('cart', {})
    total_quantity = calculate_total_cart_quantity(cart_items)
    return render_template('bikes.html', name=name, random_bikes_quote=random_quote, bike_products=_bike_products, total_quantity=total_quantity, current_page=page, total_pages=total_pages)



@usercontrol.route('/accessories')
def accessories():
    if 'email' not in session:
        return "Unauthorized access"
    mongo = PyMongo(current_app)
    user = mongo.db.users.find_one({"email": session['email']})
    
    if not user:
        return "User not found"
    
    name = user['name']
    random_quote = random.choice(accessories_quotes)
    selected_category = request.args.get('category')
    per_page = 6
    page = request.args.get('page', default=1, type=int)
    
    # Initialize total_products_count to a default value
    total_products_count = 0

    if selected_category is not None:
        selected_category = selected_category.lower()
        total_products_count = mongo.db.products.count_documents({"brand_name": selected_category})
    else:
        other_products = mongo.db.products.find({"product_name": {"$in": ["helmet", "jacket"]}})
        total_products_count = mongo.db.products.count_documents({"product_name": {"$in": ["helmet", "jacket"]}})

    total_pages = math.ceil(total_products_count / per_page)

    skip_count = (page - 1) * per_page

    if selected_category is not None:
        other_products = mongo.db.products.find({"brand_name": selected_category}).skip(skip_count).limit(per_page)
    else:
        other_products = mongo.db.products.find({"product_name": {"$in": ["helmet", "jacket"]}})
        total_products_count = mongo.db.products.count_documents({"product_name": {"$in": ["helmet", "jacket"]}})
        # Recalculate total_pages after updating total_products_count
        total_pages = math.ceil(total_products_count / per_page)

        # Calculate the skip count to skip products on previous pages
        skip_count = (page - 1) * per_page

        other_products = mongo.db.products.find({"product_name": {"$in": ["helmet", "jacket"]}}).skip(skip_count).limit(per_page)
    
    cart_items = user.get('cart', {})
    total_quantity = calculate_total_cart_quantity(cart_items)
    return render_template('accessories.html', name=name, random_accessories_quote=random_quote, other_products=other_products, current_page=page, total_quantity=total_quantity, total_pages=total_pages)

@usercontrol.route('/servicing')
def servicing():
    return render_template("servicing.html")

@usercontrol.route('/service_form', methods=['GET', 'POST'])
def service_form():
    mongo = PyMongo(current_app)
    user = mongo.db.users.find_one({"email": session['email']})
    if request.method == 'POST':
        submitted_chassis_number = request.form.get('ChassisNo')
        any_order = mongo.db.adminCart.find_one({"user_id": ObjectId(user['_id']),'status':"confirm"})
        discount = "50%" if any_order else "0%"
        mongo.db.servicing_request.insert_one(
            {
                "submitted_chassis_number": submitted_chassis_number,
                "user": user,
                "discount": discount,
                "status": "pending"
            }
        )
        services_requests = mongo.db.servicing_request.find_one({"user._id": user['_id']})
        flash("Service request submitted successfully!")

    services_requests = mongo.db.servicing_request.find_one({"user._id": user['_id']})
    return render_template("service_form.html", services_requests=services_requests)



@usercontrol.route('/order_status')
def order_status():
    mongo = PyMongo(current_app)
    
    if 'email' not in session:
        return "Unauthorized access"

    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        return "User not found"

    user_id = user["_id"]
    admin_cart_collection = mongo.db.adminCart
    order_data = admin_cart_collection.find_one({"user_id": user_id}, {"status": 1})

    if order_data:
        order_status = order_data.get("status", "")
        if order_status == "confirm":
            message = "Your order is confirmed. You will receive the product soon."
        elif order_status == "cancel":
            message = "Your order has been canceled. Please try again or contact the helpline."
        else:
            message = "Please wait for confirmation."
        cart_items = user.get('cart', {})
        total_quantity = calculate_total_cart_quantity(cart_items)
        admin_cart_collection = mongo.db.adminCart
        all_cart_items = admin_cart_collection.find({"user_id": user_id})
        return render_template("order_status.html", message=message,total_quantity=total_quantity, cart_items = all_cart_items)  #total_quantity=total_quantity
    
    return "Order data not found"


# Route for the logout functionality
@usercontrol.route("/profile_setting", methods=['GET', 'POST'])
def profile_setting():
    mongo = PyMongo(current_app)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        gender = request.form['gender']
        nid = request.form['nid']

        mongo.db.users.update_one({"email": email}, {
            "$set": {
                "name": f"{first_name} {last_name}",
                "mobile_number": phone_number,
                "address": address,
                "gender": gender,
                "nid": nid
            }
        })
        # You can also set a message here if you want to inform the user about the successful update

    # Retrieve user data to pre-fill the form for the GET request
    if 'email' in session:
        email = session['email']
        user = mongo.db.users.find_one({"email": email})
        if user:
            session['profile_update_message'] = "Profile updated successfully"
            return render_template("profile_setting.html", user=user)
    
    return render_template("profile_setting.html")

@usercontrol.route('/update_password', methods=['POST'])
def update_password():
    mongo = PyMongo(current_app)
    if 'email' not in session:
        return "Unauthorized access"

    email = session['email']
    user = mongo.db.users.find_one({"email": email})
    if not user:
        return "User not found"

    # Fetch form data
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_password')

    # Check if old password matches
    if not bcrypt.checkpw(old_password.encode('utf-8'), user['password']):
        session['login_message'] = "Incorrect password"
        flash("incorrect password")
        return render_template("profile_setting.html", user=user)  # Pass 'user' to the template here

    # Check if new passwords match
    if new_password != confirm_new_password:
        session['login_message'] = "New passwords do not match"
        flash("New passwords do not match")
        return render_template("profile_setting.html", user=user)  # Pass 'user' to the template here

    if old_password == new_password:
        session['login_message'] = "New password cannot be the same as the old password"
        flash("New password cannot be the same as the old password")
        return render_template("profile_setting.html", user=user)

    # Update password
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    mongo.db.users.update_one({"email": email}, {"$set": {"password": hashed_new_password}})

    session['login_message'] = "Password updated successfully"
    return render_template("profile_setting.html", user=user)  # Pass 'user' to the template here


@usercontrol.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# Helper function to calculate total pages for pagination
def calculate_total_pages(total_items, per_page):
    return (total_items + per_page - 1) // per_page


# Helper function to get paginated bike products
def get_paginated_bike_products(products, page, per_page):
    offset = (page - 1) * per_page
    return products.skip(offset).limit(per_page)

def get_product_image(product_id):
    mongo = PyMongo(current_app)
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    return product.get("photo_path")

def get_product_modelName(product_id):
    mongo = PyMongo(current_app)
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    return product.get("model_name")

def get_product_price(product_id):
    mongo = PyMongo(current_app)
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    return product.get("price")

@usercontrol.route('/cart')
def cart():
    mongo = PyMongo(current_app)

    if 'email' in session:
        user = mongo.db.users.find_one({"email": session['email']})

        if user:
            cart_items = user.get('cart', {})
            total_quantity = calculate_total_cart_quantity(cart_items)
            cart_total = calculate_cart_total(cart_items)  #img=img,modelName=modelName,price=price
            # img=get_product_image(product_id)
            # modelName = get_product_modelName(product_id)
            # price = get_product_price(product_id)
            product_names = [mongo.db.products.find_one({"_id": ObjectId(product_id)}).get("product_name") for product_id, cart_item in cart_items.items()]
            if 'bike' in product_names:
                shipping_charge = 2000
            elif len(product_names)>0:
                shipping_charge = 100
            else:
                shipping_charge = 0 
            total_amount = cart_total + shipping_charge
            for product_id, cart_item in cart_items.items():
                product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
                cart_item['product_modelName'] = product.get("model_name")
                cart_item['product_price'] = product.get("price")
                cart_item['photo_path'] = product.get("photo_path")
            return render_template('cart.html', cart_items=cart_items, total_quantity=total_quantity, cart_total=cart_total,shipping_charge=shipping_charge,total_amount=total_amount)

    return "Unauthorized access"

def calculate_cart_total(cart_items):
    mongo = PyMongo(current_app)
    total = 0
    for product_id, cart_item in cart_items.items():
        variable = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        product_price = int(variable.get("price"))  # Convert price to integer
        quantity = int(cart_item.get("quantity", 0))  # Convert quantity to integer
        total += product_price * quantity
    return total

@usercontrol.route('/delete_product', methods=['POST'])
def delete_product():
    print("delete_product function called")  # Add this line
    data = request.json  # Get the JSON data from the request

    if 'email' not in session:
        return jsonify({"success": False, "message": "Unauthorized access"})

    mongo = PyMongo(current_app)
    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        return jsonify({"success": False, "message": "User not found"})

    # Get the product_id from the JSON data
    product_id = data.get('product_id')

    # Remove the product from the user's cart
    if product_id in user['cart']:
        del user['cart'][product_id]
        mongo.db.users.update_one({"_id": user['_id']}, {"$set": {"cart": user['cart']}})
        return jsonify({"success": True, "message": "Product deleted successfully"})
    else:
        return jsonify({"success": False, "message": "Product not found in cart"}), 404



@usercontrol.route('/process_add_to_cart', methods=['POST'])
def process_add_to_cart():
    data = request.json

    if 'email' not in session:
        current_app.logger.warning("Unauthorized access")
        return jsonify({"success": False, "message": "Unauthorized access"})

    mongo = PyMongo(current_app)
    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        current_app.logger.warning("User not found")
        return jsonify({"success": False, "message": "User not found"})

    # Extract relevant data from request.json
    product_id = data.get('productId')
    print("Received product_id:", product_id) 
    quantity = data.get('quantity', 1)
    name = data.get('name')
    variable = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    color = variable.get("color", '')
    print("Received color:", color) 

    # Check if the product already exists in the user's cart
    if "cart" in user and product_id in user["cart"]:
        # existing_quantity = user["cart"][product_id]["quantity"]
        # new_quantity = existing_quantity + quantity
        if name == None:
            new_quantity = quantity
        else:
            existing_quantity = user["cart"][product_id]["quantity"]
            new_quantity = existing_quantity + quantity

        # Update the existing cart item's quantity
        update_query = {
            "$set": {
                f"cart.{product_id}.quantity": new_quantity
            }
        }
        mongo.db.users.update_one({"_id": user['_id']}, update_query)
        # get_cart_quantity()
        current_app.logger.info("Updated cart item quantity: %s", new_quantity)
        user = mongo.db.users.find_one({"email": session['email']})
        response = {'message': 'Item quantity updated in cart successfully', "total_products_items":sum([user['cart'][item]['quantity'] for item in user['cart']])}
    else:
        # Construct the cart item
        cart_item = {
            "quantity": quantity,
            "discount": data.get('discount', 0),  # Default discount is 0
            "color": color
        }

        # Add the new cart item
        update_query = {
            "$set": {
                f"cart.{product_id}": cart_item
            }
        }
        mongo.db.users.update_one({"_id": user['_id']}, update_query)

        current_app.logger.info("Added new item to cart: %s", cart_item)
        user = mongo.db.users.find_one({"email": session['email']})
        response = {'success': True, 'message': 'Item added to cart successfully', "total_products_items":sum([user['cart'][item]['quantity'] for item in user['cart']])}
    return jsonify(response)



@usercontrol.route('/get_user_cart', methods=['GET'])
def get_user_cart():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Unauthorized access"})

    mongo = PyMongo(current_app)
    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        return jsonify({"success": False, "message": "User not found"})

    cart = user.get('cart', {})  # Get the cart dictionary directly from the user object
    print("Retrieved cart:", cart)  # Add this debug statement

    return jsonify(cart)  # Return user's cart data (or an empty dictionary if cart doesn't exist)



def calculate_total_cart_quantity(cart_items):
    total_quantity = 0
    for cart_item in cart_items.values():
        quantity = cart_item.get("quantity", 0)
        total_quantity += int(quantity)  # Convert quantity to integer before adding
    return total_quantity




@usercontrol.route("/checkout", methods=["POST"])
def checkout():
    mongo = PyMongo(current_app)

    if 'email' not in session:
        return jsonify({"success": False, "message": "Unauthorized access"})

    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        return jsonify({"success": False, "message": "User not found"})

    data = request.form  # Use request.form to get form data

    user_id = user["_id"]
    cart_data = user.get('cart', {})
    form_data = {
        "cardholder_name": data.get('cardholder_name', ''),
        "card_number": data.get('card_number', ''),
        "expiration": data.get('expiration', ''),
        "cvv": data.get('cvv', '')
    }
    payment_type = data.get('payment_type')
    total_amount = float(data.get('total_amount', 0))

    # Insert checkout data into the adminCart collection
    admin_cart_collection = mongo.db.adminCart
    checkout_data = {
        'user_id': user_id,
        'cart_data': cart_data,
        'form_data': form_data,
        'payment_type': payment_type,
        'total_amount': total_amount,
        'status': ""
    }
    admin_cart_collection.insert_one(checkout_data)

    # Simulate deleting user's cart
    mongo.db.users.update_one({"_id": user_id}, {"$unset": {"cart": 1}})

    return jsonify({"success": True, "message": "Order placed successfully"})


@usercontrol.route("/all_orders", methods=['GET'])
def all_orders():
    mongo = PyMongo(current_app) 
    if 'email' not in session:
        return jsonify({"success": False, "message": "Unauthorized access"})

    user = mongo.db.users.find_one({"email": session['email']})

    if not user:
        return jsonify({"success": False, "message": "User not found"})

    user_id = user["_id"]
    # user_id = ObjectId('65748c8fd652bdad1e0ccab1')
    #Retrieve cart data from the adminCart collection
    admin_cart_collection = mongo.db.adminCart
    cart_items = admin_cart_collection.find({"user_id": ObjectId(user_id)}) 
    # return jsonify(cart_items) 
    return render_template("order_status.html", cart_items=cart_items)


# ... (your existing code)




