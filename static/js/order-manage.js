document.querySelector('.order-form').addEventListener("submit", async (e) => {
    e.preventDefault();
    const signInErrorMsg = document.querySelector("#signInErrorMsg");

    signInErrorMsg.textContent = ""; // Очистим предыдущие ошибки

    const formData = new FormData(e.target);
    const data = {
        user_id: formData.get('user_id'), // Пример для user_id, если есть
        type_id: formData.get('category'), // Пример для type_id, соответствующий выбору категории
        comment: formData.get('comments'),
        files: formData.get('url') // Ссылка на файл или строка
    };

    try {
        // Отправляем данные на сервер
        const response = await fetch("/add_order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            signInErrorMsg.style.color = "#38a169"; // Зеленый для успешного добавления
            signInErrorMsg.textContent = result.message; // Сообщение о успешном добавлении

            // Сбросим форму
            e.target.reset();

            // Обновим страницу через 1 секунду (например, чтобы дать время для отображения сообщения)
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
