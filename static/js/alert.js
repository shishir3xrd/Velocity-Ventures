function checker(name) {
    var result = confirm('Are you sure, ' + name + '?');
    if (result == false) {
        event.preventDefault();
        return false; // Prevent the default action of the link
    }
    return true; // Allow the link to proceed
}