const optionItems = document.getElementById("option-types");
const shownOptions = []

function showData(event) {
    if(event.target.parentElement.nextElementSibling.classList.contains("hidden")){
        event.target.parentElement.nextElementSibling.classList.remove("hidden")
        event.target.nextElementSibling.classList.remove("hidden");
        hideCards(event);
        if(shownOptions[0]){
            shownOptions[0].classList.add("hidden");
            shownOptions[0] = event.target.parentElement.nextElementSibling;
        }
        else
            shownOptions.push(event.target.parentElement.nextElementSibling);
    }
}

function hideCards(event){
    optionItems.childNodes.forEach(innerDiv => {
        if(innerDiv.dataset){
            if(innerDiv.dataset.option === 'card' && innerDiv !== event.target.parentElement){
                innerDiv.classList.add("hidden");
            }
            else if(innerDiv.dataset.option === 'card' && innerDiv === event.target.parentElement){
                optionItems.classList.remove("library-flex");
                innerDiv.classList.remove("library-card");
                innerDiv.firstElementChild.classList.add("hidden");
            }
        }
    })
}

function reloadPage(event){
    location.reload()
}


optionItems.childNodes.forEach(innerDiv => {
    if(innerDiv.dataset){
        if(innerDiv.dataset.option === "card"){
            innerDiv.firstElementChild.addEventListener("click", showData);
            innerDiv.firstElementChild.nextElementSibling.addEventListener("click", reloadPage)
        }
    }
});
