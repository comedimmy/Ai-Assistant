function sendData() {
    let inputText = document.getElementById("userInput").value;

    let jsonData = {
        "message": inputText
    };

    fetch("http://127.0.0.1:5000/api/send-mqtt", {
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
    fetch("/api/get_user_data", {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("錯誤：" + data.error);
        } else {
            alert(`使用者資訊：
            姓名：${data.nickname}
			登入方式:${data.Login_type}
            最後登入時間：${data.Last_login}`);
        }
    })
    .catch(error => console.error("發生錯誤", error));
}


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

        fetch("/api/update_user_name", {
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
    console.log("頁面載入完成，開始獲取使用者資料和水族箱列表");

    // 獲取使用者資料
    fetch("/api/get_user_data")
    .then(response => response.json())
    .then(data => {
        if (data.nickname) {
            document.getElementById("userNameBox").value = data.nickname;
        }
    })
    .catch(error => {
        console.error("獲取使用者資料失敗：", error);
    });
	
};


// 顯示或隱藏選單
function openMenu(aquarium_id) {
    const menu = document.getElementById(`menu-${aquarium_id}`);
    menu.classList.toggle('active');  // 切換選單的顯示狀態
}



// 修改水族箱名稱
function editAquariumName(aquarium_id) {
    const newName = prompt("請輸入新的水族箱名稱:");
    if (newName) {
        // 呼叫後端 API 更新水族箱名稱
        fetch(`/api/update_aquarium_name/${aquarium_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ new_name: newName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("水族箱名稱已更新！");
                location.reload();  // 重新載入頁面以顯示更新後的名稱
            } else {
                alert("更新失敗，請稍後再試！");
            }
        });
    }
}

// 刪除水族箱
function deleteAquarium(aquarium_id) {
    if (confirm("確定要刪除這個水族箱嗎？")) {
        fetch(`/api/delete_aquarium/${aquarium_id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("水族箱已刪除！");
                location.reload();  // 重新載入頁面以顯示刪除後的結果
            } else {
                alert("刪除失敗，請稍後再試！");
            }
        });
    }
}

document.querySelectorAll('.aquarium-link').forEach(function(link) {
    link.addEventListener('click', function(event) {
        event.preventDefault(); // 防止頁面重整

        const aquariumId = link.getAttribute('data-aquarium-id');  // 獲取水族箱的 UUID
        
        // 發送 GET 請求，獲取水族箱詳細資訊
        fetch(`/api/get_aquarium_details/${aquariumId}`)
            .then(response => response.json())
            .then(data => {
                window.location.href = `/aqur_console?aquarium_id=${aquariumId}`;
            })
            .catch(error => {
                console.error('獲取水族箱詳細資訊失敗:', error);
            });
    });
});