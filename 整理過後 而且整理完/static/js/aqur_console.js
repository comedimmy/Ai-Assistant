// 從 URL 擷取水族箱 ID
const urlParams = new URLSearchParams(window.location.search);
const aquariumId = urlParams.get('aquarium_id');


// 確保取得 ID 並在 API 請求中傳送
document.getElementById('capture').addEventListener('click', function() {
    html2canvas(document.getElementById('capture-area'), { useCORS: true }).then(function(canvas) {
        const imageData = canvas.toDataURL("image/png");
		const urlParams = new URLSearchParams(window.location.search);
		const aquariumId = urlParams.get('aquarium_id');
		
        fetch(`/api/save_snapshot/${aquariumId}`, {
            method: 'POST',
            body: JSON.stringify({ image: imageData, aquarium_id: aquariumId }),  // 傳送水族箱 ID
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => console.log('圖片已儲存', data))
        .catch(error => console.error('圖片儲存失敗', error));
    });
});
document.getElementById("fetchDetailsBtn").addEventListener("click", function () {
    // 從網址取得參數
    const urlParams = new URLSearchParams(window.location.search);
    const aquariumId = urlParams.get("aquarium_id");

    if (!aquariumId) {
        alert("找不到 aquarium_id");
        return;
    }

    // 用 GET 發送 fetch 請求
    fetch(`/api/get_aquarium_details/${aquariumId}`)
        .then(response => {
            if (!response.ok) throw new Error("伺服器錯誤");
            return response.json();
        })
        .then(data => {
            console.log("水族箱資料：", data);
            document.getElementById("result").innerText = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error("錯誤：", error);
            document.getElementById("result").innerText = "取得資料失敗";
        });
});

document.getElementById("update_button").addEventListener("click", function() {
    const newName = document.getElementById("new_name").value;
    
    // 檢查是否有輸入新名稱
    if (!newName) {
      alert("請輸入新名稱");
      return;
    }

    // 假設水族箱 ID 是從 URL 中獲取的
    const aquariumId = new URLSearchParams(window.location.search).get('aquarium_id');

    // 發送更新請求
    fetch(`/api/update_aquarium_name/${aquariumId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ new_name: newName })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert("水族箱名稱更新成功！");
      } else {
        alert("更新失敗：" + data.message);
      }
    })
    .catch(error => {
      console.error("錯誤：", error);
      alert("發生錯誤，請稍後再試");
    });
  });
  
document.getElementById("update_settings_button").addEventListener("click", function() {
    const formData = new FormData(document.getElementById("update-settings-form"));
    const data = {};

    // 將表單資料轉換為 JSON 格式
    formData.forEach((value, key) => {
        if (key === 'light_status') {
            // 如果是燈光狀態，轉換為數字 0 或 1
            data[key] = parseInt(value);
        } else {
            data[key] = value;
        }
    });

    const aquariumId = new URLSearchParams(window.location.search).get('aquarium_id');

    fetch(`/api/update_aquarium/${aquariumId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("水族箱設定更新成功！");
        } else {
            alert("更新失敗：" + data.message);
        }
    })
    .catch(error => console.error("錯誤：", error));
});


function goToPageMessage() {
    const aquariumId = new URLSearchParams(window.location.search).get("aquarium_id");
    if (aquariumId) {
        window.location.href = `/message?aquarium_id=${aquariumId}`;
    } else {
        alert("找不到 aquarium_id！");
    }
}