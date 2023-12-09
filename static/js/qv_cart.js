

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

