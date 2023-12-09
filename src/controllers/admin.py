from flask import Blueprint, render_template, flash, redirect, url_for, request,current_app
from flask_pymongo import PyMongo
from bson import ObjectId
import os
from werkzeug.utils import secure_filename

from src.utils import send_servicing_email

admincontrol = Blueprint("admin", __name__, template_folder="templates")
current_dir = os.path.dirname(os.path.abspath(__file__))

# Update the UPLOAD_FOLDER to the path where you want to store uploaded photos
UPLOAD_FOLDER = os.path.join('static', 'product_img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admincontrol.route("/admin_dashboard", methods=['GET'])
def admin_dashboard():
    mongo = PyMongo(current_app)
    total_products = mongo.db.products.count_documents({})
    total_users = mongo.db.users.count_documents({})
    total_cart = mongo.db.adminCart.count_documents({})
    return render_template("admin_dashboard.html",total_products=total_products,total_cart=total_cart,total_users=total_users)

@admincontrol.route("/admin_addproduct", methods=['GET'])
def admin_addproduct():
    return render_template("admin_addproduct.html")



@admincontrol.route("/admin_Manproduct", methods=['GET'])
def admin_Manproduct():
    mongo = PyMongo(current_app)
    all_products = mongo.db.products.find()  # Retrieve all products from the database
    return render_template("admin_Manproduct.html", all_products=all_products)



@admincontrol.route("/product_upload", methods=['POST'])
def process_admin_form():
    mongo = PyMongo(current_app)
    product_name = request.form.get('product-name').lower()
    brand_name = request.form.get('brand-name').lower() 
    model_name = request.form.get('model-name')
    product_description = request.form.get('product-description')
    price = request.form.get('price')
    color = request.form.get('color')
    discount = request.form.get('discount')
    warranty = request.form.get('warranty')
    
    # Get the uploaded photo
    photo = request.files.get('photo')

    if photo and allowed_file(photo.filename):
        # Save the photo with a unique name in the UPLOAD_FOLDER
        filename = secure_filename(photo.filename)
        photo_path = os.path.join('product_img', filename).replace(os.sep, '/')
        # Get the absolute path to the static folder in the current app context
        static_folder = os.path.abspath(current_app.static_folder)

        # Combine the static folder path with the upload folder path to get the final save path
        save_path = os.path.join(static_folder, photo_path)

        # Save the file
        photo.save(os.path.join(current_app.root_path, save_path))

        # Store the form data in the database
        product_data = {
            "product_name": product_name,
            "brand_name": brand_name,
            "model_name": model_name,
            "product_description": product_description,
            "price": price,
            "color": color,
            "warranty": warranty,
            "discount": discount,
            "photo_path": photo_path
        }
        # Insert the data into the MongoDB collection (replace 'products' with your collection name)
        mongo = PyMongo(current_app)
        mongo.db.products.insert_one(product_data)

        # Flash a success message and redirect to the same page
        flash('Product uploaded successfully!', 'success')
        return redirect(url_for('admin.admin_addproduct'))

    # If the file is not allowed or there was an error, render the admin dashboard page
    flash('Invalid file! Allowed file types: png, jpg, jpeg, gif', 'error')
    return redirect(url_for('admin.admin_addproduct'))

@admincontrol.route("/admin.delete_product/<product_id>", methods=['GET'])
def delete_product(product_id):
    mongo = PyMongo(current_app)
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    if product:
        # Delete the product from the database
        mongo.db.products.delete_one({"_id": ObjectId(product_id)})
        flash(f"Product '{product['product_name']}' deleted successfully", 'success')
    else:
        flash("Product not found", 'error')

    return redirect(url_for('admin.admin_Manproduct'))


@admincontrol.route("/admin.admin_manageProduct/<product_id>", methods=['GET', 'POST'])
def manageProduct(product_id):
    mongo = PyMongo(current_app)

    if request.method == 'GET':
        # Retrieve the existing product details from the database
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        
        if not product:
            # Handle case when product is not found
            return "Product not found", 404

        return render_template('admin_manageProduct.html', product=product)

    if request.method == 'POST':
        updated_fields = {}
        for field_name in ['model_name', 'price', 'color', 'product_description', 'discount']:
            updated_value = request.form.get(field_name)
            if updated_value:
                updated_fields[field_name] = updated_value

        if updated_fields:
            # Update the user's fields in the database
            mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": updated_fields})
        
        return redirect(url_for('admin.admin_Manproduct'))
        
        
    return render_template('admin_manageProduct.html', product=product)



@admincontrol.route("/admin_manageUser/<user_id>", methods=['GET', 'POST'])
def admin_manageUser(user_id):
    mongo = PyMongo(current_app)
    
    if request.method == 'GET':
        # Convert user_id to ObjectId to query MongoDB
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            # Handle case when user is not found
            return "User not found", 404

    if request.method == 'POST':
        updated_fields = {}
        
        for field_name in ['name', 'nid', 'mobile_number', 'address', 'gender']:
            updated_value = request.form.get(field_name)
            if updated_value:
                updated_fields[field_name] = updated_value
        
        if updated_fields:
            # Update the user's fields in the database
            mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_fields})
        
        return redirect(url_for('admin.admin_Manuser'))

    return render_template('admin_manageUser.html', user=user)

@admincontrol.route("/admin_Manuser", methods=['GET'])
def admin_Manuser():
    mongo = PyMongo(current_app)
    all_users = mongo.db.users.find()
    return render_template("admin_Manuser.html", all_info=all_users)

@admincontrol.route("/admin_Mancart", methods=['GET'])
def admin_Mancart():
    mongo = PyMongo(current_app)
    
    # Retrieve cart data from the adminCart collection
    admin_cart_collection = mongo.db.adminCart
    cart_items = admin_cart_collection.find()

    # Process cart data to include additional details
    processed_cart_items = []
    for cart_item in cart_items:
        user_id = cart_item.get("user_id")
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        cart_item['user_name'] = user.get("name")
        processed_cart_items.append(cart_item)

    return render_template("admin_Mancart.html", cart_items=processed_cart_items)


@admincontrol.route("/admin_Servicing", methods=['GET'])
def admin_Servicing():
    mongo = PyMongo(current_app)
    
    # Retrieve cart data from the adminCart collection
    servicing_request_collection = mongo.db.servicing_request
    servicing_requests = servicing_request_collection.find()

    # Process cart data to include additional details
    _servicing_requests = []
    for servicing_request in servicing_requests:
        _servicing_requests.append(servicing_request)

    return render_template("admin_Servicing.html", servicing_requests=_servicing_requests)

@admincontrol.route("/admin_update_discount", methods=['GET'])
def admin_update_discount():
    mongo = PyMongo(current_app)
    servicing_id = request.values.get("servicing_id")
    discount = request.values.get("discount")
    # Retrieve cart data from the adminCart collection
    servicing_request_collection = mongo.db.servicing_request
    servicing_requests = servicing_request_collection.update_one({"_id":ObjectId(servicing_id)}, {"$set":{
        "discount": discount
    }})
    servicing_requests = servicing_request_collection.find()
    # Process cart data to include additional details
    _servicing_requests = []
    for servicing_request in servicing_requests:
        _servicing_requests.append(servicing_request)

    return redirect(url_for('admin.admin_Servicing'))

@admincontrol.route("/admin_confirm_servicing", methods=['GET'])
def admin_confirm_servicing():
    from server import mail
    mongo = PyMongo(current_app)
    servicing_id = request.values.get("servicing_id")
    # Retrieve cart data from the adminCart collection
    servicing_request_collection = mongo.db.servicing_request
    servicing_request = servicing_request_collection.update_one({"_id":ObjectId(servicing_id)}, {"$set":{
        "status": "Accepted for Servicing"
    }})
    servicing_request = servicing_request_collection.find_one({"_id":ObjectId(servicing_id)})
    send_servicing_email(mail, servicing_request['user'], "Accepted for Servicing", servicing_request['status'])
    servicing_requests = servicing_request_collection.find()
    # Process cart data to include additional details
    _servicing_requests = []
    for servicing_request in servicing_requests:
        _servicing_requests.append(servicing_request)

    return redirect(url_for('admin.admin_Servicing'))
    
@admincontrol.route("/admin_reject_servicing", methods=['GET'])
def admin_reject_servicing():
    from server import mail
    mongo = PyMongo(current_app)
    
    servicing_id = request.values.get("servicing_id")
    # Retrieve cart data from the adminCart collection
    servicing_request_collection = mongo.db.servicing_request
    servicing_requests = servicing_request_collection.update_one({"_id":ObjectId(servicing_id)}, {"$set":{
        "status": "Rejected for Servicing"
    }})
    servicing_request = servicing_request_collection.find_one({"_id":ObjectId(servicing_id)})
    send_servicing_email(mail, servicing_request['user'], "Rejected for Servicing", servicing_request['status'])
    servicing_requests = servicing_request_collection.find()
    # Process cart data to include additional details
    _servicing_requests = []
    for servicing_request in servicing_requests:
        _servicing_requests.append(servicing_request)

    return redirect(url_for('admin.admin_Servicing'))

@admincontrol.route("/admin_delete_servicing", methods=['GET'])
def admin_delete_servicing():
    mongo = PyMongo(current_app)
    
    servicing_id = request.values.get("servicing_id")
    # Retrieve cart data from the adminCart collection
    servicing_request_collection = mongo.db.servicing_request
    servicing_requests = servicing_request_collection.delete_one({"_id":ObjectId(servicing_id)})
    servicing_requests = servicing_request_collection.find()
    # Process cart data to include additional details
    _servicing_requests = []
    for servicing_request in servicing_requests:
        _servicing_requests.append(servicing_request)

    return redirect(url_for('admin.admin_Servicing'))



@admincontrol.route("/admin_confirm_cart/<string:cart_id>", methods=['GET'])
def admin_confirm_cart(cart_id):
    mongo = PyMongo(current_app)

    # Update the cart status to "confirm"
    admin_cart_collection = mongo.db.adminCart
    admin_cart_collection.update_one({"_id": ObjectId(cart_id)}, {"$set": {"status": "confirm"}})

    return redirect(url_for('admin.admin_Mancart'))

@admincontrol.route("/admin_cancel_cart/<string:cart_id>", methods=['GET'])
def admin_cancel_cart(cart_id):
    mongo = PyMongo(current_app)

    # Update the cart status to "cancel"
    admin_cart_collection = mongo.db.adminCart
    admin_cart_collection.update_one({"_id": ObjectId(cart_id)}, {"$set": {"status": "cancel"}})

    return redirect(url_for('admin.admin_Mancart'))

@admincontrol.route("/admin_delete_cart/<string:cart_id>", methods=['GET'])
def admin_delete_cart(cart_id):
    mongo = PyMongo(current_app)

    # Delete the cart
    admin_cart_collection = mongo.db.adminCart
    admin_cart_collection.delete_one({"_id": ObjectId(cart_id)})

    return redirect(url_for('admin.admin_Mancart'))
