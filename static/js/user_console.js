function sendData() {
    let inputText = document.getElementById("userInput").value;

    let jsonData = {
        "message": inputText
    };

    fetch("http://127.0.0.1:5000/send-mqtt", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        const displayElement = document.createElement('div');
        displayElement.textContent = "回應：" + JSON.stringify(data);
        document.body.appendChild(displayElement);
    })
    .catch(error => console.error("錯誤:", error));
}
function typeWriterEffect(text, elementId, speed = 50) {
    let index = 0;
    const element = document.getElementById(elementId);
    element.textContent = "";

    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, speed);
        }
    }
    type();
}

// 顯示或隱藏聊天視窗
function toggleChatBox() {
    var chatBox = document.getElementById('chat-box');
    if (chatBox.style.display === 'none' || chatBox.style.display === '') {
        chatBox.style.display = 'block'; // 顯示視窗
    } else {
        chatBox.style.display = 'none'; // 隱藏視窗
    }
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendChatMessage();
    }
}

function sendChatMessage() {
    var inputElement = document.getElementById('chat-input');
    var message = inputElement.value.trim();
    if (message === '') return; // 忽略空訊息

    var chatBoxBody = document.getElementById('chat-box-body');

    // 顯示使用者的訊息
    var userMessage = document.createElement('div');
    userMessage.textContent = "您: " + message;
    chatBoxBody.appendChild(userMessage);
    inputElement.value = ''; // 清空輸入框
    chatBoxBody.scrollTop = chatBoxBody.scrollHeight;

    // 顯示 "思考中..."
    var typingEffect = document.createElement('div');
    typingEffect.id = "typing-effect";
    typingEffect.textContent = "思考中";
    chatBoxBody.appendChild(typingEffect);
    chatBoxBody.scrollTop = chatBoxBody.scrollHeight;

    let dots = 0;
    const loadingInterval = setInterval(() => {
        if (dots < 3) {
            typingEffect.textContent += ".";
            dots++;
        } else {
            typingEffect.textContent = "思考中";
            dots = 0;
        }
    }, 1000);

    // 發送訊息到後端
    let jsonData = { "message": message };
    fetch("http://127.0.0.1:5000/receive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(loadingInterval);
        typingEffect.remove(); // 移除 "思考中..."

        // 顯示 AI 回覆
        var aiMessage = document.createElement('div');
        aiMessage.textContent = "AI管家: " + data.result;
        chatBoxBody.appendChild(aiMessage);
        chatBoxBody.scrollTop = chatBoxBody.scrollHeight;  // 滾動到底部
    })
    .catch(error => {
        clearInterval(loadingInterval);
        typingEffect.textContent = "發生錯誤，請稍後再試！";
        console.error("錯誤:", error);
    });
}

function getUserData() {
    fetch("/get_user_data", {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("錯誤：" + data.error);
        } else {
            alert(`使用者資訊：
            姓名：${data.UserName}
            Email：${data.Email || "N/A"}
            註冊時間：${data.LastLoginTime}`);
        }
    })
    .catch(error => console.error("發生錯誤", error));
}

// 從 URL 擷取水族箱 ID
const urlParams = new URLSearchParams(window.location.search);
const aquariumId = urlParams.get('aquarium_id');

// 確保取得 ID 並在 API 請求中傳送
document.getElementById('capture').addEventListener('click', function() {
    html2canvas(document.getElementById('capture-area'), { useCORS: true }).then(function(canvas) {
        const imageData = canvas.toDataURL("image/png");

        fetch('/save_snapshot', {
            method: 'POST',
            body: JSON.stringify({ image: imageData, aquarium_id: aquariumId }),  // 傳送水族箱 ID
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => console.log('圖片已儲存', data))
        .catch(error => console.error('圖片儲存失敗', error));
    });
});





let isEditing = false;

function toggleEdit() {
    let userNameBox = document.getElementById("userNameBox");
    let editButton = document.getElementById("editButton");

    if (!isEditing) {
        // 進入編輯模式
        userNameBox.removeAttribute("readonly");
        editButton.textContent = "保存";
    } else {
        // 保存新名稱
        let newName = userNameBox.value;

        fetch("/update_user_name", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_name: newName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("錯誤：" + data.error);
            } else {
                alert("名稱已更新：" + data.new_name);
                userNameBox.setAttribute("readonly", true);
                editButton.textContent = "修改";
            }
        })
        .catch(error => console.error("發生錯誤", error));
    }

    isEditing = !isEditing;
}

// **載入當前的 user_name**
window.onload = function() {
    fetch("/get_user_data")  // 這個 API 在之前已經寫過
    .then(response => response.json())
    .then(data => {
        if (data.UserName) {
            document.getElementById("userNameBox").value = data.UserName;
        }
    });
};
