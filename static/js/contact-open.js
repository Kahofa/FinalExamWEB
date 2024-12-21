document.getElementById('contactButton').addEventListener('click', function(event) {
    event.preventDefault();
  
    var contactMenu = document.getElementById('contactMenu');
    if (contactMenu.style.display === 'block') {
      contactMenu.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => {
        contactMenu.style.display = 'none';
        contactMenu.style.animation = '';
      }, 10);
    } else {
      contactMenu.style.display = 'block';
      contactMenu.style.animation = 'slideIn 0.3s ease-out';
    }
  });