/* =========================================
   ECONOMICS TEST SYSTEM
========================================= */

const QUESTIONS_PER_TEST = 10;

const TOTAL_QUESTIONS = 1000;

const TOTAL_TESTS = 100;

const STORAGE_KEY = "economicTestUser";


/* =========================================
   STATE
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

const loginPage =
    document.getElementById("loginPage");

const homePage =
    document.getElementById("homePage");

const testPage =
    document.getElementById("testPage");

const resultPage =
    document.getElementById("resultPage");


const phoneInput =
    document.getElementById("phoneInput");

const phoneError =
    document.getElementById("phoneError");

const loginButton =
    document.getElementById("loginButton");

const logoutButton =
    document.getElementById("logoutButton");

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

document.addEventListener(
    "DOMContentLoaded",
    () => {

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

    }
);


/* =========================================
   LOAD USER
========================================= */

function loadUser() {

    const saved =
        localStorage.getItem(
            STORAGE_KEY
        );


    if (!saved) {

        showPage(loginPage);

        return;

    }


    try {

        userData =
            JSON.parse(saved);


        if (!userData.phone) {

            showPage(loginPage);

            return;

        }


        showPage(homePage);

        updateHome();


    } catch (error) {

        console.error(error);

        localStorage.removeItem(
            STORAGE_KEY
        );

        showPage(loginPage);

    }

}


/* =========================================
   LOGIN
========================================= */

function login() {

    const digits =
        phoneInput.value.replace(
            /\D/g,
            ""
        );


    phoneError.textContent = "";


    if (digits.length !== 10) {

        phoneError.textContent =
            "Введите 10 цифр номера телефона.";

        return;

    }


    const phone =
        "+7 " +
        digits.substring(0, 3) +
        " " +
        digits.substring(3, 6) +
        " " +
        digits.substring(6, 8) +
        " " +
        digits.substring(8, 10);


    userData = {

        phone: phone,

        currentTest: 1,

        currentQuestion: 0,

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

    let digits =
        event.target.value.replace(
            /\D/g,
            ""
        );


    digits =
        digits.substring(0, 10);


    let formatted = "";


    if (digits.length > 0) {

        formatted =
            digits.substring(0, 3);

    }


    if (digits.length >= 4) {

        formatted +=
            " " +
            digits.substring(3, 6);

    }


    if (digits.length >= 7) {

        formatted +=
            " " +
            digits.substring(6, 8);

    }


    if (digits.length >= 9) {

        formatted +=
            " " +
            digits.substring(8, 10);

    }


    event.target.value =
        formatted;

}


/* =========================================
   SAVE
========================================= */

function saveUser() {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(userData)
    );

}


/* =========================================
   PAGE
========================================= */

function showPage(page) {

    document
        .querySelectorAll(".page")
        .forEach(
            pageElement => {

                pageElement.classList.remove(
                    "active"
                );

            }
        );


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


    const percent =
        Math.round(
            (
                userData.completedTests /
                TOTAL_TESTS
            ) * 100
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
        userData.completedTests;


    document.getElementById(
        "totalTests"
    ).textContent =
        TOTAL_TESTS;


    document.getElementById(
        "completedQuestions"
    ).textContent =
        userData.completedQuestions;


    document.getElementById(
        "totalQuestions"
    ).textContent =
        TOTAL_QUESTIONS;


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
        "N" +
        userData.currentTest;


    document.getElementById(
        "currentTestQuestion"
    ).textContent =
        "10 вопросов";

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
   GET QUESTION
========================================= */

function getCurrentQuestion() {

    const globalIndex =
        (
            (currentTestNumber - 1) *
            QUESTIONS_PER_TEST
        ) +
        currentQuestionIndex;


    return questions[globalIndex];

}


/* =========================================
   RENDER
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
        "N" +
        currentTestNumber;


    document.getElementById(
        "questionCounter"
    ).textContent =
        "Вопрос " +
        questionNumber +
        " из 10";


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
                () => {

                    selectAnswer(
                        button,
                        letter,
                        question.correct
                    );

                }
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
        questionNumber === 10
    ) {

        nextButton.innerHTML =
            `
            Завершить N${currentTestNumber}
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
   ANSWER
========================================= */

function selectAnswer(
    selectedButton,
    selectedAnswer,
    correctAnswer
) {

    if (answerSelected) return;


    answerSelected = true;


    const buttons =
        document.querySelectorAll(
            ".answer-button"
        );


    buttons.forEach(
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


        buttons.forEach(
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
        currentQuestionIndex >= 10
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

    userData.totalCorrect +=
        currentCorrect;


    userData.totalWrong +=
        currentWrong;


    userData.completedQuestions +=
        10;


    userData.completedTests =
        currentTestNumber;


    userData.lastScore =
        currentScore;


    userData.currentQuestion =
        0;


    saveUser();


    document.getElementById(
        "resultTestNumber"
    ).textContent =
        "N" +
        currentTestNumber;


    document.getElementById(
        "resultScore"
    ).textContent =
        currentScore +
        "/10";


    document.getElementById(
        "resultCorrect"
    ).textContent =
        currentCorrect;


    document.getElementById(
        "resultWrong"
    ).textContent =
        currentWrong;


    const percent =
        currentScore * 10;


    document.querySelector(
        ".result-percent"
    ).textContent =
        percent + "%";


    if (
        currentTestNumber <
        TOTAL_TESTS
    ) {

        const nextNumber =
            currentTestNumber + 1;


        nextTestButton.innerHTML =
            `
            Перейти к N${nextNumber}
            <span>→</span>
            `;


        nextTestButton.disabled =
            false;


    } else {

        nextTestButton.innerHTML =
            `
            Все тесты завершены ✓
            `;


        nextTestButton.disabled =
            true;

    }


    showPage(resultPage);

}


/* =========================================
   NEXT TEST
========================================= */

function nextTest() {

    if (
        currentTestNumber >=
        TOTAL_TESTS
    ) {

        return;

    }


    currentTestNumber++;


    currentQuestionIndex = 0;


    currentScore = 0;

    currentCorrect = 0;

    currentWrong = 0;


    userData.currentTest =
        currentTestNumber;


    userData.currentQuestion =
        0;


    saveUser();


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
       Прогресс НЕ удаляется.
       Поэтому после повторного входа
       пользователь продолжит с текущего N.
    */


    userData = null;


    phoneInput.value = "";


    showPage(loginPage);

}
