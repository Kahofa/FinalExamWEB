const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');

    const selectElement = document.getElementById('category');
    if (category) {
      selectElement.value = category; 
    }