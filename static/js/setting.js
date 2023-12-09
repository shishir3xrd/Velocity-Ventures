document.addEventListener("DOMContentLoaded", function () {
    const editProfileButton = document.getElementById("edit-profile");
    const cancelEditButton = document.getElementById("cancel-edit");
    const profileInfo = document.getElementById("profile-info");
    const editProfileInfo = document.getElementById("edit-profile-info");

    // Show the edit profile form and hide the profile info
    editProfileButton.addEventListener("click", function () {
        profileInfo.style.display = "none";
        editProfileInfo.style.display = "block";
    });

    // Cancel editing and show the profile info
    cancelEditButton.addEventListener("click", function () {
        profileInfo.style.display = "block";
        editProfileInfo.style.display = "none";
    });

    // Add client-side validation logic if needed
    // For example, you can check if the password and confirm-password fields match.
});
