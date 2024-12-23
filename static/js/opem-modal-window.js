document.querySelector('.order-form').addEventListener("submit", async (e) => {
    e.preventDefault();

    const signInErrorMsg = document.querySelector("#signInErrorMsg");
    signInErrorMsg.textContent = "";

    const formData = new FormData(e.target);

    formData.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });

    try {
        const response = await fetch("/add_order", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            signInErrorMsg.style.color = "#38a169";
            signInErrorMsg.textContent = result.message;

            e.target.reset();

            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            signInErrorMsg.style.color = "#e53e3e";
            signInErrorMsg.textContent = result.message;
        }
    } catch (error) {
        signInErrorMsg.style.color = "#e53e3e";
        signInErrorMsg.textContent = "Произошла ошибка. Попробуйте позже.";
    }
});
