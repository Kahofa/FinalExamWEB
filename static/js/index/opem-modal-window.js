const openModalBtn = document.getElementById('openModalBtn');
    const closeModalBtn = document.getElementById('closeModal');
    const loginModal = document.getElementById('loginModal');

    loginModal.style.display = 'block';

    openModalBtn.addEventListener('click', () => {
      loginModal.style.display = 'block';
    });

    closeModalBtn.addEventListener('click', () => {
      loginModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
      if (e.target === loginModal) {
        loginModal.style.display = 'none';
      }
    });