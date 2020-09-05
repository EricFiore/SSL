function setButtons(){
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener("click", () => {
            const topBar = button.parentElement;
            const tabsContainer = topBar.parentElement;
            const tabID = button.dataset.forResults;
            const tabToActivate = tabsContainer.querySelector(`.results-section[data-results="${tabID}"]`);

            tabsContainer.querySelectorAll(".results-section").forEach(tab => {
                tab.classList.remove("active-tab");
                tab.classList.add("hidden");
            });

            tabToActivate.classList.add("active-tab")
            tabToActivate.classList.remove("hidden")
        })
    })
}

document.addEventListener("DOMContentLoaded", () => {
    setButtons();

    document.querySelectorAll("#tab-container").forEach(tabsContainer => {
        tabsContainer.querySelector(".results-buttons .btn").click();
    })
})