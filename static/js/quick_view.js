 
// quick view js 
 function populateQuickViewModal(button) {
    var modal = $('#quickViewModal');
    var productId = button.data('product');
    var photo = button.data('photo');
    var name = button.data('name');
    var price = button.data('price');
    var description = button.data('description');
    var warranty = button.data('warranty');

    // Populate modal elements with data
    modal.find('#quickViewPhoto').attr('src', photo);
    modal.find('#quickViewName').text(name);
    modal.find('#quickViewDescription').text(description);
    modal.find('#quickViewPrice').text(price + ' TK');;

    // Open the modal
    modal.modal('show');
}

