document.addEventListener("DOMContentLoaded", () => {
    const translations = {
        ru: {
            fillAllFields: "Пожалуйста, заполните все поля!",
            passwordTooShort: "Пароль должен содержать минимум 4 символа!",
            successfulRegistration: "Успешная регистрация!",
            successfulLogin: "Успешный вход!"
        },
        kz: {
            fillAllFields: "Please fill in all fields!",
            passwordTooShort: "Password must be at least 4 characters long!",
            successfulRegistration: "Registration successful!",
            successfulLogin: "Login successful!"
        }
    };

    let currentLanguage = "ru";

    const signUpForm = document.getElementById("signUpForm");
    const signInForm = document.getElementById("signInForm");

    const signUpNameInput = document.getElementById("name");
    const signUpEmailInput = document.getElementById("email");
    const signUpPasswordInput = document.getElementById("signUpPassword");
    const signUpErrorMsg = document.getElementById("signUpErrorMsg");

    const signInNameInput = document.getElementById("signInName");
    const signInPasswordInput = document.getElementById("signInPassword");
    const signInErrorMsg = document.getElementById("signInErrorMsg");

    const languageButtons = document.querySelectorAll(".multilang-btn");

    languageButtons.forEach(button => {
        button.addEventListener("click", () => {
            currentLanguage = button.id;
            languageButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");
        });
    });

    signUpForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        signUpErrorMsg.textContent = "";

        const username = signUpNameInput.value.trim();
        const email = signUpEmailInput.value.trim();
        const password = signUpPasswordInput.value.trim();

        if (!username || !email || !password) {
            signUpErrorMsg.textContent = "Пожалуйста, заполните все поля.";
            shakeForm(signUpForm);
            return;
        }

        if (password.length < 4) {
            signUpErrorMsg.textContent = "Пароль слишком короткий.";
            shakeForm(signUpForm);
            return;
        }

        signUpErrorMsg.style.color = "#38a169";
        signUpErrorMsg.textContent = "Регистрация прошла успешно. Пожалуйста, подождите...";

        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password }),
            });

            const result = await response.json();

            if (result.success) {
                signUpErrorMsg.style.color = "#38a169";
                signUpErrorMsg.textContent = result.message;

                setTimeout(() => {
                    window.location.href = "/";
                }, 1000);
            } else {
                signUpErrorMsg.style.color = "#e53e3e";
                signUpErrorMsg.textContent = result.message;
                shakeForm(signUpForm);
            }
        } catch (error) {
            signUpErrorMsg.style.color = "#e53e3e";
            signUpErrorMsg.textContent = "Произошла ошибка. Попробуйте позже.";
        }
    });

    signInForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        signInErrorMsg.textContent = "";

        const username = signInNameInput.value.trim();
        const password = signInPasswordInput.value.trim();

        if (!username || !password) {
            signInErrorMsg.textContent = "Пожалуйста, заполните все поля.";
            shakeForm(signInForm);
            return;
        }

        if (password.length < 4) {
            signInErrorMsg.textContent = "Пароль слишком короткий.";
            shakeForm(signInForm);
            return;
        }

        try {
            console.log("Отправляемые данные:", { username, password });

            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const result = await response.json();

            if (result.success) {
                signInErrorMsg.style.color = "#38a169";
                signInErrorMsg.textContent = result.message;

                setTimeout(() => {
                    window.location.href = "/";
                }, 1000);
            } else {
                signInErrorMsg.style.color = "#e53e3e";
                signInErrorMsg.textContent = result.message;
                shakeForm(signInForm);
            }
        } catch (error) {
            signInErrorMsg.style.color = "#e53e3e";
            signInErrorMsg.textContent = "Произошла ошибка. Попробуйте позже.";
        }
    });

    function shakeForm(form) {
        form.classList.add("shake");
        setTimeout(() => form.classList.remove("shake"), 300);
    }

    function clearErrorMsg(errorElement) {
        setTimeout(() => {
            errorElement.textContent = "";
        }, 3000);
    }
});
