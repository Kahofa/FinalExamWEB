document.querySelector('.order-form').addEventListener("submit", async (e) => {
    e.preventDefault();
    const orderError = document.querySelector("#orderError");

    orderError.textContent = "";

    const formData = new FormData(e.target);
    const data = {
        user_id: formData.get('user_id'),
        type_id: formData.get('category'),
        comment: formData.get('comments'),
        files: formData.get('url')
    };

    try {

        const response = await fetch("/add_order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            orderError.style.color = "#38a169";
            orderError.textContent = result.message;
            e.target.reset();
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            orderError.style.color = "#e53e3e";
            orderError.textContent = result.message;
        }

    } catch (error) {
        orderError.style.color = "#e53e3e";
        orderError.textContent = "Произошла ошибка. Попробуйте позже.";
    }
});
