function setUpTabs() {
    document.querySelectorAll(".btn").forEach(button =>{
        button.addEventListener("click", () =>{
            const topBar = button.parentElement;
            const tabsContainer = topBar.parentElement;
            const tabNumber = button.dataset.forTab;
            const tabToActivate = tabsContainer.querySelector(`.tab[data-tab="${tabNumber}"]`);

            tabsContainer.querySelectorAll(".tab").forEach(tab =>{
                tab.classList.remove("active-tab");
            });

            tabToActivate.classList.add("active-tab");
        })
    })
}

document.addEventListener("DOMContentLoaded", () => {
    setUpTabs();

    document.querySelectorAll(".card").forEach(tabsContainer => {
        tabsContainer.querySelector(".btn-group .btn").click();
    });
})

function getSiblings(firstNode, requestingNode){
    let siblings = [];
    let workingNode = firstNode
    for ( ; workingNode; workingNode = workingNode.nextElementSibling){
        if (workingNode.nodeType === 1 && workingNode !== requestingNode){
            siblings.push(workingNode);
        }
    }
    return siblings
}