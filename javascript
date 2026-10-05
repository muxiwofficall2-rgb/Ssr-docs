function loadUser() {

    const saved = localStorage.getItem(STORAGE_KEY);

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

        localStorage.removeItem(STORAGE_KEY);

        showPage(loginPage);
    }
}
