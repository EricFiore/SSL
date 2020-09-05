const firmwareList = document.getElementById("list-of-firmware");

firmwareList.childNodes.forEach(div => {
    if(div.nodeType === Node.ELEMENT_NODE){
        div.lastElementChild.firstElementChild.firstElementChild.addEventListener("mouseover", placeCover);
        div.lastElementChild.firstElementChild.childNodes[3].addEventListener("mouseout", removeCover);
    }
})

function placeCover(event){
    const changesOuterDiv = getOuterDiv(event.target);
    const targetHeight = changesOuterDiv.offsetHeight;
    changesOuterDiv.classList.add("hidden");
    changesOuterDiv.nextElementSibling.classList.remove("hidden");
    changesOuterDiv.nextElementSibling.style.height = targetHeight + "px";
    changesOuterDiv.nextElementSibling.style.lineHeight = targetHeight + "px";
}

function removeCover(event){
    event.target.classList.add("hidden");
    event.target.previousElementSibling.classList.remove("hidden");
}

function getOuterDiv(divElement){
    let changesOuterDiv = divElement;
    let loopCounter = 0;
    while(changesOuterDiv.dataset.firmwareContent !== "changes-outer-div"){
        changesOuterDiv = changesOuterDiv.parentElement;
        loopCounter += 1;
        if(loopCounter === 200)
            break;
    }
    return changesOuterDiv;
}