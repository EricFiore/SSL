function setUpForm(){
    const form = document.getElementById("page-form")
    setProperHeights(findFormElements(form));
}

function setProperHeights(formItems) {
    if(!formItems)
        return

    let labels = {};
    let inputs = {};

    for(let element of formItems){
        if(element.dataset.form.startsWith('label'))
            labels[getLastWord(element.dataset.form)] = element;
        else if(element.dataset.form.startsWith('input'))
            inputs[getLastWord(element.dataset.form)] = element.offsetHeight;
    }

    for(const [key, value] of Object.entries(labels)){
        labels[key].style.height = inputs[key] + "px";
    }
}

function getLastWord(dataSet){
    const splitDataSet = dataSet.split('-');
    return splitDataSet[splitDataSet.length - 1];
}

function findFormElements(item){
    let formItems = []
    for(let i= 0; i < item.childNodes.length; i++){
        if(item.hasChildNodes() && item.childNodes[i].nodeType === Node.ELEMENT_NODE){
            let inputs = findFormElements(item.childNodes[i])
            if(Array.isArray(inputs)){
                for(let j = 0; j < inputs.length; j++){
                    formItems.push(inputs[j])
                }
            }
            else{
                formItems.push(inputs)
            }
        }
        else if(item.dataset.form){
            return item;
        }
    }
    if(formItems.length)
        return formItems;
    return null
}

document.addEventListener("DOMContentLoaded", () => {
    setUpForm();
})