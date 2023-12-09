$(document).ready(function() {
    $("#checkout-btn").click(function() {
        // Collect form data
        var formData = {
            cardholder_name: $("#typeName").val(),
            card_number: $("#typeText").val(),
            expiration: $("#typeExp").val(),
            cvv: $("#typeCvv").val(),
            payment_type: $("select[name='payment_type']").val(), // Updated this line
            total_amount: parseFloat($("#totalAmount").text().replace("$", ""))
        };

        // Send AJAX request to process checkout
        $.ajax({
            url: "/user/checkout", // Update the URL to your checkout route
            type: "POST",
            data: formData,
            success: function(response) {
                // Handle success response
                if (response.success) {
                    // Redirect to a success page or show a success message
                    window.location.href = "/user/order_status";
                } else {
                    // Show an error message
                    alert("Checkout failed: " + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error(error);
                console.log(xhr.responseText);
                alert("An error occurred during checkout.");
            }
        });
    });
});
