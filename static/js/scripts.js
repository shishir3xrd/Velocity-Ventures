window.addEventListener('DOMContentLoaded', event => {
  // Navbar shrink function
  var navbarShrink = function () {
      const navbarCollapsible = document.body.querySelector('#mainNav');
      if (!navbarCollapsible) {
          return;
      }
      if (window.scrollY === 0) {
          navbarCollapsible.classList.remove('navbar-shrink')
      } else {
          navbarCollapsible.classList.add('navbar-shrink')
      }
  };

  // Shrink the navbar 
  navbarShrink();

  // Shrink the navbar when page is scrolled
  document.addEventListener('scroll', navbarShrink);

  // Activate Bootstrap scrollspy on the main nav element
  const mainNav = document.body.querySelector('#mainNav');
  if (mainNav) {
      new bootstrap.ScrollSpy(document.body, {
          target: '#mainNav',
          rootMargin: '0px 0px -40%',
      });
  };

  // Collapse responsive navbar when toggler is visible
  const navbarToggler = document.body.querySelector('.navbar-toggler');
  const responsiveNavItems = [].slice.call(document.querySelectorAll('#navbarResponsive .nav-link'));
  responsiveNavItems.map(function (responsiveNavItem) {
      responsiveNavItem.addEventListener('click', () => {
          if (window.getComputedStyle(navbarToggler).display !== 'none') {
              navbarToggler.click();
          }
      });
  });
});

// Function to open the login popup
function openLoginPopup() {
  document.getElementById('loginPopup').classList.add('active-popup');
}

// Function to close the login popup
function closeLoginPopup() {
  document.getElementById('loginPopup').classList.remove('active-popup');
}

// Function to open the register popup
function openRegisterPopup() {
  document.getElementById('registerPopup').classList.add('active-popup');
}


function closeRegisterPopup() {
  document.getElementById('registerPopup').classList.remove('active-popup');
}

function openLoginPopup() {
  document.getElementById('loginPopup').classList.add('active-popup');
}

// Function to close the login popup
function closeLoginPopup() {
  document.getElementById('loginPopup').classList.remove('active-popup');
}

// Function to open the register popup
function openRegisterPopup() {
  document.getElementById('registerPopup').classList.add('active-popup');
}

// Function to close the register popup
function closeRegisterPopup() {
  document.getElementById('registerPopup').classList.remove('active-popup');
}

// Function to open the error message popup
    
document.addEventListener('DOMContentLoaded', function () {
  var loginMessage = document.getElementById("loginMessage").value;

  if (loginMessage !== "") {
    // Show the popup
    document.getElementById("loginMessagePopup").style.display = "block";

    // Add click event listener to the close button
    document.getElementById("closeLoginMessagePopup").addEventListener("click", function () {
      // Hide the popup when the close button is clicked
      document.getElementById("loginMessagePopup").style.display = "none";
    });
  }
});

