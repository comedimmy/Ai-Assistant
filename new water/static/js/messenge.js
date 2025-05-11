
const msg = document.getElementById("msg_input").value;
// 從 URL 擷取水族箱 ID
const urlParams = new URLSearchParams(window.location.search);
const aquariumId = urlParams.get('aquarium_id');

fetch(`/api/send_messenge/${aquariumId}`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ messenge: msg })
})
.then(res => res.json())
.then(data => {
    console.log("GPT 回覆:", data.GPT_messenge);
});

function sendToGPT() {
    const msg = document.getElementById("msg_input").value;
    
    fetch(`/api/send_messenge/${aquariumId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ messenge: msg })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("gpt_response").innerText = data.GPT_messenge || data.error;
    });
}