const errorSearch = document.getElementById('error-search');
const manualModels = document.getElementById('manual-models');
const manualFixes = document.getElementById('manual-fixes');
const tipModels = document.getElementById('tip-models');
const tipFixes = document.getElementById('tip-fixes');
const customModels = document.getElementById('custom-models')
const customFixes = document.getElementById('custom-fixes')

const manualModelsDict = {};
const manualModelsArray = [];
const tipModelsDict = {};
const tipModelsArray = [];
const customModelsDict = {};
const customModelsArray = [];

const MANID = 'man-'
const TIPID = 'tip-'
const CUSTID = 'cust-'

manualModels.childNodes.forEach(value => {
    getFixData(manualModelsDict, manualModelsArray, value);
});

tipModels.childNodes.forEach(value => {
    getFixData(tipModelsDict, tipModelsArray, value);
});

customModels.childNodes.forEach(value => {
    getFixData(customModelsDict, customModelsArray, value)
});

function getFixData(modelsDict, modelsArray, items){
    const separatedString = items.textContent.split('`')
    if(separatedString[1]){
        modelsDict[separatedString[0].toLowerCase().replace(/(\r\n|\n|\r| )/g, "")]
            = separatedString[1];
        modelsArray.push(separatedString[0].toLowerCase().replace(/(\r\n|\n|\r| )/g, ""));
    }
}

function listSolutions(items, modelsDict, idType, clearType){
    clearList(clearType);
    let testSolution = null;
    for(item in items){
        if(modelsDict[items[item]] !== testSolution){
            testSolution = modelsDict[items[item]];
            const model = items[item].toString();
            const solutionDiv = document.getElementById(idType + model)
            solutionDiv.classList.remove('hidden');
        }
    }
}

function clearList(clearType){
    const divsToClear = clearType.childNodes.forEach(value => {
        if(value.classList){
            if(!value.classList.contains('hidden'))
                value.classList.add('hidden');
        }
    });
}

errorSearch.addEventListener('input', (event) => {
    let searchTerm = event.target.value;
    if(searchTerm && searchTerm.trim().length > 0){
        searchTerm = searchTerm.trim().toLowerCase();
        listSolutions(manualModelsArray.filter(value => {
            return value.includes(searchTerm);
        }), manualModelsDict, MANID, manualFixes);
        listSolutions(tipModelsArray.filter(value => {
            return value.includes(searchTerm);
        }), tipModelsDict, TIPID, tipFixes);
        listSolutions(customModelsArray.filter(value => {
            return value.includes(searchTerm);
        }), customModelsDict, CUSTID, customFixes);
    }
    else if(searchTerm.trim().length === 0){
        clearList(manualFixes);
        clearList(tipFixes);
        clearList(customFixes);
    }
});

document.querySelectorAll(".error-detail-outer-wrapper").forEach(div => {
    div.addEventListener('mouseenter', () => {
        div.childNodes.forEach(accordionNode => {
            if(accordionNode.className === 'accordion'){
                console.log(accordionNode.style);
                if(accordionNode.style.maxHeight !== accordionNode.scrollHeight + 'px'){
                    accordionNode.style.maxHeight = accordionNode.scrollHeight + 'px';
                }
            }
        })
    });
});

document.querySelectorAll(".error-detail-outer-wrapper").forEach(div => {
    div.addEventListener('mouseleave', () => {
        div.childNodes.forEach(accordionNode => {
            if(accordionNode.className === 'accordion'){
                if(accordionNode.style.maxHeight === accordionNode.scrollHeight + 'px'){
                    accordionNode.style.maxHeight = 0 + 'px';
                }
            }
        })
    });
});