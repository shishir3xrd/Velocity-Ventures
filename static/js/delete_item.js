$('.delete-product').on('click', function(e) {
    e.preventDefault();
    var productId = $(this).data('product-id');
    console.log(' id :',productId);
    $.ajax({
        type: 'POST',
        url: '/user/delete_product',
        contentType: 'application/json',
        data: JSON.stringify({ product_id: productId }),
        
        success: function(response) {
            console.log('Delete product response:', response); 
            // Reload the page after successful deletion
            window.location.reload();
        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
});
