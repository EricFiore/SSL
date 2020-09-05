const messageContainer = document.querySelector("#new-message-container");
const messageForm = document.querySelector("#new-message-form");
const replyLink = document.querySelectorAll('.message-reply-button')
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll("[data-reply]").forEach( option => {
        option.hidden = true;
    })
    document.querySelector('#new-message').addEventListener("click", showNewMessageForm);
    replyLink.forEach(formContainer => {
        formContainer.addEventListener("click", showReplyMessageForm);
    });
})

function showNewMessageForm(){
    console.log(messageForm.firstElementChild.scrollHeight);
    if (messageForm.classList.contains("hidden")){
        messageForm.classList.remove("hidden");
        messageContainer.style.Height = messageForm.scrollHeight + 'px';
    }
    else{
        messageForm.classList.add("hidden");
        messageContainer.style.Height = 0 + 'px';
    }
}

function showReplyMessageForm(){
    document.querySelectorAll(".reply-message-container").forEach(div => {
        if (div.id !== "reply-message-" + this.dataset.id){
            div.classList.add("hidden")
        }
    })
    const replyDiv = document.getElementById("reply-message-" + this.dataset.id);
    const sendTo = document.getElementById("send-to-" + this.dataset.id).firstElementChild;
    if (replyDiv.classList.contains("hidden")){
        replyDiv.classList.remove("hidden");
        const receiver = sendTo.parentElement.dataset.reply;
        for (let i =0; i < sendTo.options.length; i++){
            if (receiver === sendTo.options[i].text){
                sendTo.options[i].selected = true;
                break;
            }
        }
    }
    else{
        replyDiv.classList.add("hidden");
    }
}
