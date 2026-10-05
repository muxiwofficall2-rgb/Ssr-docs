/* =========================================
   ECONOMIC TEST
   MAIN JAVASCRIPT
========================================= */


/* =========================================
   SETTINGS
========================================= */

const QUESTIONS_PER_TEST = 10;


/* =========================================
   STORAGE
========================================= */

const STORAGE_KEY = "economicTestUser";


/* =========================================
   GLOBAL STATE
========================================= */

let userData = null;

let currentQuestionIndex = 0;

let currentTestNumber = 1;

let currentScore = 0;

let currentCorrect = 0;

let currentWrong = 0;

let answerSelected = false;


/* =========================================
   DOM
========================================= */

const loginPage = document.getElementById("loginPage");
const homePage = document.getElementById("homePage");
const testPage = document.getElementById("testPage");
const resultPage = document.getElementById("resultPage");

const phoneInput = document.getElementById("phoneInput");
const phoneError = document.getElementById("phoneError");

const loginButton = document.getElementById("loginButton");

const logoutButton = document.getElementById("logoutButton");

const continueButton =
    document.getElementById("continueButton");

const backHomeButton =
    document.getElementById("backHomeButton");

const nextButton =
    document.getElementById("nextButton");

const nextTestButton =
    document.getElementById("nextTestButton");

const resultHomeButton =
    document.getElementById("resultHomeButton");


/* =========================================
   START
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    loadUser();

    phoneInput.addEventListener(
        "input",
        formatPhone
    );

    loginButton.addEventListener(
        "click",
        login
    );

    continueButton.addEventListener(
        "click",
        startTest
    );

    logoutButton.addEventListener(
        "click",
        logout
    );

    backHomeButton.addEventListener(
        "click",
        () => {
            showPage(homePage);
            updateHome();
        }
    );

    nextButton.addEventListener(
        "click",
        nextQuestion
    );

    nextTestButton.addEventListener(
        "click",
        nextTest
    );

    resultHomeButton.addEventListener(
        "click",
        () => {
            showPage(homePage);
            updateHome();
        }
    );

});


/* =========================================
   LOAD USER
========================================= */

function loadUser() {

    const saved =
        localStorage.getItem(STORAGE_KEY);

    if (!saved) {

        showPage(loginPage);

        return;
    }

    try {

        userData = JSON.parse(saved);

        if (!userData.phone) {

            showPage(loginPage);

            return;
        }

        showPage(homePage);

        updateHome();

    } catch (error) {

        console.error(error);

        localStorage.removeItem(STORAGE_KEY);

        showPage(loginPage);
    }

}


/* =========================================
   LOGIN
========================================= */

function login() {

    const phone =
        normalizePhone(phoneInput.value);

    phoneError.textContent = "";

    if (phone.length < 10) {

        phoneError.textContent =
            "Введите корректный номер телефона.";

        return;
    }


    userData = {

        phone: phone,

        currentQuestion: 0,

        currentTest: 1,

        totalCorrect: 0,

        totalWrong: 0,

        completedTests: 0,

        completedQuestions: 0,

        lastScore: 0

    };


    saveUser();

    showPage(homePage);

    updateHome();

}


/* =========================================
   PHONE FORMAT
========================================= */

function formatPhone(event) {

    let value =
        event.target.value.replace(/\D/g, "");

    if (value.startsWith("8")) {

        value = "7" + value.substring(1);
    }

    if (value.startsWith("7")) {

        value = value.substring(1);
    }

    value = value.substring(0, 10);


    let formatted = "";

    if (value.length > 0) {

        formatted += value.substring(0, 3);
    }

    if (value.length >= 4) {

        formatted += " " +
            value.substring(3, 6);
    }

    if (value.length >= 7) {

        formatted += " " +
            value.substring(6, 8);
    }

    if (value.length >= 9) {

        formatted += " " +
            value.substring(8, 10);
    }

    event.target.value = formatted;

}


function normalizePhone(value) {

    let digits =
        value.replace(/\D/g, "");

    if (digits.startsWith("8")) {

        digits =
            "7" + digits.substring(1);
    }

    if (!digits.startsWith("7")) {

        digits =
            "7" + digits;
    }

    return "+" + digits;

}


/* =========================================
   SAVE USER
========================================= */

function saveUser() {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(userData)
    );

}


/* =========================================
   SHOW PAGE
========================================= */

function showPage(page) {

    document
        .querySelectorAll(".page")
        .forEach(item => {

            item.classList.remove("active");

        });

    page.classList.add("active");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* =========================================
   HOME
========================================= */

function updateHome() {

    if (!userData) return;


    document.getElementById(
        "userPhoneDisplay"
    ).textContent =
        userData.phone;


    const totalTests =
        Math.ceil(
            questions.length /
            QUESTIONS_PER_TEST
        );


    const completed =
        userData.completedTests;


    const percent =
        Math.round(
            (completed / totalTests) * 100
        );


    document.getElementById(
        "progressPercent"
    ).textContent =
        percent + "%";


    document.getElementById(
        "progressBar"
    ).style.width =
        percent + "%";


    document.getElementById(
        "completedTests"
    ).textContent =
        completed;


    document.getElementById(
        "totalTests"
    ).textContent =
        totalTests;


    document.getElementById(
        "completedQuestions"
    ).textContent =
        userData.completedQuestions;


    document.getElementById(
        "totalQuestions"
    ).textContent =
        questions.length;


    document.getElementById(
        "correctTotal"
    ).textContent =
        userData.totalCorrect;


    document.getElementById(
        "wrongTotal"
    ).textContent =
        userData.totalWrong;


    document.getElementById(
        "currentTestTitle"
    ).textContent =
        "Тест №" + userData.currentTest;


    const questionInTest =
        userData.currentQuestion + 1;


    document.getElementById(
        "currentTestQuestion"
    ).textContent =
        "Вопрос " +
        questionInTest +
        " из " +
        QUESTIONS_PER_TEST;

}


/* =========================================
   START TEST
========================================= */

function startTest() {

    currentTestNumber =
        userData.currentTest;

    currentQuestionIndex =
        userData.currentQuestion;

    currentScore = 0;

    currentCorrect = 0;

    currentWrong = 0;

    answerSelected = false;

    showPage(testPage);

    renderQuestion();

}


/* =========================================
   GET CURRENT QUESTION
========================================= */

function getCurrentQuestion() {

    const globalIndex =
        (
            currentTestNumber - 1
        ) *
            QUESTIONS_PER_TEST +
        currentQuestionIndex;


    return questions[globalIndex];

}


/* =========================================
   RENDER QUESTION
========================================= */

function renderQuestion() {

    const question =
        getCurrentQuestion();


    if (!question) {

        finishTest();

        return;
    }


    answerSelected = false;


    const questionNumber =
        currentQuestionIndex + 1;


    document.getElementById(
        "testNumber"
    ).textContent =
        "Тест №" + currentTestNumber;


    document.getElementById(
        "questionCounter"
    ).textContent =
        "Вопрос " +
        questionNumber +
        " из " +
        QUESTIONS_PER_TEST;


    document.getElementById(
        "questionNumber"
    ).textContent =
        questionNumber;


    document.getElementById(
        "questionText"
    ).textContent =
        question.question;


    document.getElementById(
        "currentScore"
    ).textContent =
        currentScore;


    const progress =
        (
            questionNumber /
            QUESTIONS_PER_TEST
        ) * 100;


    document.getElementById(
        "questionProgressFill"
    ).style.width =
        progress + "%";


    const answersContainer =
        document.getElementById(
            "answersContainer"
        );


    answersContainer.innerHTML = "";


    Object.entries(
        question.answers
    ).forEach(
        ([letter, answer]) => {

            const button =
                document.createElement(
                    "button"
                );


            button.className =
                "answer-button";


            button.dataset.answer =
                letter;


            button.innerHTML = `

                <span class="answer-letter">
                    ${letter}
                </span>

                <span>
                    ${answer}
                </span>

            `;


            button.addEventListener(
                "click",
                () => selectAnswer(
                    button,
                    letter,
                    question.correct
                )
            );


            answersContainer.appendChild(
                button
            );

        }
    );


    nextButton.disabled = true;

    nextButton.classList.add(
        "disabled"
    );


    if (
        questionNumber ===
        QUESTIONS_PER_TEST
    ) {

        nextButton.innerHTML =
            `
            Завершить тест
            <span>✓</span>
            `;

    } else {

        nextButton.innerHTML =
            `
            Следующий вопрос
            <span>→</span>
            `;
    }

}


/* =========================================
   SELECT ANSWER
========================================= */

function selectAnswer(
    selectedButton,
    selectedAnswer,
    correctAnswer
) {

    if (answerSelected) return;

    answerSelected = true;


    const allButtons =
        document.querySelectorAll(
            ".answer-button"
        );


    allButtons.forEach(
        button => {

            button.classList.add(
                "disabled"
            );

        }
    );


    if (
        selectedAnswer ===
        correctAnswer
    ) {

        selectedButton.classList.add(
            "correct"
        );

        currentCorrect++;

        currentScore++;


    } else {

        selectedButton.classList.add(
            "wrong"
        );

        currentWrong++;


        allButtons.forEach(
            button => {

                if (
                    button.dataset.answer ===
                    correctAnswer
                ) {

                    button.classList.add(
                        "correct"
                    );

                }

            }
        );

    }


    document.getElementById(
        "currentScore"
    ).textContent =
        currentScore;


    nextButton.disabled = false;

    nextButton.classList.remove(
        "disabled"
    );

}


/* =========================================
   NEXT QUESTION
========================================= */

function nextQuestion() {

    if (!answerSelected) return;


    currentQuestionIndex++;


    userData.currentQuestion =
        currentQuestionIndex;


    saveUser();


    if (
        currentQuestionIndex >=
        QUESTIONS_PER_TEST
    ) {

        finishTest();

        return;
    }


    renderQuestion();

}


/* =========================================
   FINISH TEST
========================================= */

function finishTest() {

    const testScore =
        currentScore;


    userData.totalCorrect +=
        currentCorrect;


    userData.totalWrong +=
        currentWrong;


    userData.completedQuestions +=
        QUESTIONS_PER_TEST;


    userData.completedTests++;


    userData.lastScore =
        testScore;


    userData.currentQuestion = 0;


    saveUser();


    document.getElementById(
        "resultScore"
    ).textContent =
        currentScore +
        "/" +
        QUESTIONS_PER_TEST;


    document.getElementById(
        "resultCorrect"
    ).textContent =
        currentCorrect;


    document.getElementById(
        "resultWrong"
    ).textContent =
        currentWrong;


    const percent =
        Math.round(
            (
                currentScore /
                QUESTIONS_PER_TEST
            ) * 100
        );


    document.querySelector(
        ".result-percent"
    ).textContent =
        percent + "%";


    const totalTests =
        Math.ceil(
            questions.length /
            QUESTIONS_PER_TEST
        );


    if (
        userData.completedTests >=
        totalTests
    ) {

        nextTestButton.textContent =
            "Все тесты завершены ✓";

        nextTestButton.disabled = true;

    } else {

        nextTestButton.innerHTML =
            `
            Перейти к следующему тесту
            <span>→</span>
            `;

        nextTestButton.disabled = false;

    }


    showPage(resultPage);

}


/* =========================================
   NEXT TEST
========================================= */

function nextTest() {

    const totalTests =
        Math.ceil(
            questions.length /
            QUESTIONS_PER_TEST
        );


    if (
        userData.currentTest >=
        totalTests
    ) {

        return;
    }


    userData.currentTest++;

    userData.currentQuestion = 0;

    saveUser();


    currentTestNumber =
        userData.currentTest;

    currentQuestionIndex = 0;

    currentScore = 0;

    currentCorrect = 0;

    currentWrong = 0;


    showPage(testPage);

    renderQuestion();

}


/* =========================================
   LOGOUT
========================================= */

function logout() {

    const confirmed =
        confirm(
            "Вы действительно хотите выйти?"
        );


    if (!confirmed) return;


    /*
       ВАЖНО:
       Мы НЕ удаляем прогресс.

       Поэтому при повторном входе
       на этом же устройстве данные
       останутся.
    */

    userData = null;

    phoneInput.value = "";

    showPage(loginPage);

}
