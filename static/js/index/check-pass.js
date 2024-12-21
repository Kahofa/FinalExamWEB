document.addEventListener("DOMContentLoaded", () => {
    const translations = {
        ru: {
            fillAllFields: "Пожалуйста, заполните все поля!",
            passwordTooShort: "Пароль должен содержать минимум 6 символов!",
            successfulRegistration: "Успешная регистрация!",
            successfulLogin: "Успешный вход!"
        },
        kz: {
            fillAllFields: "Please fill in all fields!",
            passwordTooShort: "Password must be at least 6 characters long!",
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

    signUpForm.addEventListener("submit", (e) => {
        e.preventDefault();
        signUpErrorMsg.textContent = "";

        if (!signUpNameInput.value || !signUpEmailInput.value || !signUpPasswordInput.value) {
            signUpErrorMsg.textContent = translations[currentLanguage].fillAllFields;
            shakeForm(signUpForm);
            clearErrorMsg(signUpErrorMsg);
            return;
        }

        if (signUpPasswordInput.value.length < 6) {
            signUpErrorMsg.textContent = translations[currentLanguage].passwordTooShort;
            shakeForm(signUpForm);
            clearErrorMsg(signUpErrorMsg);
            return;
        }

        signUpErrorMsg.style.color = "#38a169";
        signUpErrorMsg.textContent = translations[currentLanguage].successfulRegistration;
    });

    signInForm.addEventListener("submit", (e) => {
        e.preventDefault();
        signInErrorMsg.textContent = "";

        if (!signInNameInput.value || !signInPasswordInput.value) {
            signInErrorMsg.textContent = translations[currentLanguage].fillAllFields;
            shakeForm(signInForm);
            clearErrorMsg(signInErrorMsg);
            return;
        }

        if (signInPasswordInput.value.length < 6) {
            signInErrorMsg.textContent = translations[currentLanguage].passwordTooShort;
            shakeForm(signInForm);
            clearErrorMsg(signInErrorMsg);
            return;
        }

        signInErrorMsg.style.color = "#38a169";
        signInErrorMsg.textContent = translations[currentLanguage].successfulLogin;
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
