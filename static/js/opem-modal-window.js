document.querySelector('.order-form').addEventListener("submit", async (e) => {
    e.preventDefault();

    const signInErrorMsg = document.querySelector("#signInErrorMsg");
    signInErrorMsg.textContent = ""; // Очистить все предыдущие ошибки

    const formData = new FormData(e.target);

    // Логируем содержимое формы перед отправкой
    formData.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });

    try {
        // Отправляем данные на сервер с помощью fetch
        const response = await fetch("/add_order", {
            method: "POST",
            body: formData,  // FormData автоматически определяет правильный content-type
        });

        const result = await response.json();

        if (response.ok) {
            signInErrorMsg.style.color = "#38a169"; // Зеленый для успешного добавления
            signInErrorMsg.textContent = result.message; // Сообщение об успешном добавлении

            // Сбросим форму
            e.target.reset();

            // Перезагрузим страницу через 1 секунду (можно поменять время на ваше усмотрение)
            setTimeout(() => {
                location.reload(); // Перезагружаем страницу
            }, 1000);
        } else {
            signInErrorMsg.style.color = "#e53e3e"; // Красный для ошибки
            signInErrorMsg.textContent = result.message; // Сообщение об ошибке
        }

    } catch (error) {
        signInErrorMsg.style.color = "#e53e3e"; // Красный для ошибки
        signInErrorMsg.textContent = "Произошла ошибка. Попробуйте позже.";
    }
});
