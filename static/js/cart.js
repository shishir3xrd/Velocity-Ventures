$('.add-to-cart').on('click', function (e) {
    e.preventDefault();
    var button = $(this);

    $.ajax({
        url: '/user/get_user_cart',
        method: 'GET',
        success: function(userCart) {
            // Extract data attributes from the button
            var productId = button.data('product');
            var photo = button.data('photo');
            var name = button.data('name');
            var color = button.data('color');
            var discount = button.data('discount');
            var price = button.data('price');
            var description = button.data('description');
            var warranty = button.data('warranty');
            if (checkIfProductInCart(userCart, productId)) {
                if (!confirm("This product is already in your cart. Do you want to update the quantity?")) {
                    return false;
                }
            }
            
            // Create an object to send to the server
            var dataToSend = {
                productId: productId,
                photo: photo,
                name: name,
                discount: discount,
                color: color,
                price: price,
                description: description,
                warranty: warranty
            };

            // Send the data to the Flask route using an AJAX request
            console.log('Data to send:', dataToSend);
            console.log(' id :',productId);
            $.ajax({
                url: '/user/process_add_to_cart',
                method: 'POST',
                contentType: 'application/json',  // Specify JSON content type
                data: JSON.stringify(dataToSend), // Convert data to JSON
                success: function(response) {
                    var messageContainer = button.closest('.product').find('.message-container');
                    if (response.success) {
                        var successMessage = 'Product "' + name + '" added to cart successfully!';
                        messageContainer.html(successMessage);
                        messageContainer.addClass('success').removeClass('error');
                    } else {
                        var errorMessage = displayError('Product "' + name + '" quantity incremented!');
                        messageContainer.html(errorMessage);
                        messageContainer.removeClass('success').addClass('error'); 
                    }
                    console.log(response);
                    document.getElementById('n_cart_items').innerHTML = `[${response.total_products_items}]`
                }
            });
        },
        error: function(xhr, status, error) {
            var errorMessage = displayError('An error occurred: ' + error);
            var messageContainer = button.closest('.product').find('.message-container');
            messageContainer.html(errorMessage);
        }
    });
});

function addToCart(userCart,product_id) {
    // Check if the product is already in the cart
    if (checkIfProductInCart(userCart,product_id)) {
        if (!confirm("This product is already in your cart. Do you want to update the quantity?")) {
            return false;
        }
    }
}

function checkIfProductInCart(userCart, product_id) {
    if (userCart && userCart[product_id]) {
        return true; // Product is already in the cart
    }
    
    return false; // Product is not in the cart
}

function displayMessage(message, isSuccess) {
    var messageContainer = $('#message-container');
    messageContainer.removeClass('success error'); // Remove existing classes
    if (isSuccess) {
        messageContainer.addClass('success').text(message);
    } else {
        messageContainer.addClass('error').text(message);
    }
    setTimeout(function() {
        messageContainer.empty(); // Clear the message after a few seconds
    },5000); // Adjust the time (in milliseconds) as needed
}

function displayError(message) {
    var errorElement = $('<div>').addClass('message error').text(message);
    return errorElement;
}




// Listen for the click event on quick view buttons
$('.quick-view-btn').on('click', function (e) {
    e.preventDefault();
    populateQuickViewModal($(this));
});



$('.quick-view-btn').on('click', function () {
    var productId = $(this).data('product');
    var productName = $(this).data('name');
    var productPrice = parseFloat($(this).data('price'));
    var color = $(this).data('color');
    $('#quickViewModal').data('color', color);
    $('#quickViewModal').data('product', productId);
    $('#quickViewModal').data('productName', productName);
    $('#quickViewModal').data('productPrice', productPrice);
});

$('#quickViewModal').on('click', '.btn-primary', function () {
    var productId = $('#quickViewModal').data('product');
    var productName = $('#quickViewModal').data('productName');
    var quantity = parseInt($('#quickViewQuantity').val());
    var color = $('#quickViewModal').data('color');

    // Here, you can add the product to the cart and update the cart display as needed
    addToCart(productId, quantity, color, function(response) {
        if (response.success) {
            alert('Added ' + quantity + ' ' + productName + ' to cart.');
        } else {
            var message = 'Error adding ' + productName + ' to cart.';
            var isSuccess = false;
            var displayDuration = 2000; // 2 seconds in milliseconds
            displayMessage(message, isSuccess, $('.message-container'), displayDuration);
        }

        updateCartQuantity(productId, quantity, function(response) {
            if (response.success) {
                alert('Updated quantity of ' + productName + ' to ' + quantity + ' in cart.');
            } else {
                var message = 'Error updating quantity of ' + productName + ' in cart.';
                var isSuccess = false;
                var displayDuration = 2000; // 2 seconds in milliseconds
                displayMessage(message, isSuccess, $('.message-container'), displayDuration);
            }
        });
    });

    // Close the quick view modal
    $('#quickViewModal').modal('hide');
});

function addToCart(productId, quantity, color, callback) {
    var dataToSend = {
        productId: productId,
        quantity: quantity,
        color: color
    };
    $.ajax({
        url: '/user/process_add_to_cart',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(dataToSend),
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            console.error('An error occurred:', error);
            callback({ success: false });
        }
    });
}

