const urlParams = new URLSearchParams(window.location.search);
const aquariumId = urlParams.get('aquarium_id');

document.ElementById("send_messenge_to_AI").addEventListener("submit", function(event) {
   
		
    // 發送 POST 請求到後端
    fetch('/api/add_messenge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            aqurium_id: aquariumId,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        // 顯示返回的資料
        const resultDiv = document.getElementById("result");
        
        if (data.error) {
            resultDiv.innerHTML = `<p>錯誤: ${data.error}</p>`;
        } else {
            // 填入返回的資料
            document.getElementById("min_temp").value = `${data.min_temp}`;
            document.getElementById("max_temp").value = `${data.max_temp}`;
            document.getElementById("feeding_frequency").value = `${data.feeding_frequency}`;
            document.getElementById("feeding_amount").value = `${data.feeding_amount} `;
            
            // 停止載入動畫
            form.classList.remove("loading");
            
            // 顯示結果並顯示確認表單
            document.getElementById("modalOverlay").style.display = "block";
            document.getElementById("result").style.display = "block";
            
            // 當點擊背景遮罩時，關閉彈窗
			document.getElementById("modalOverlay").addEventListener("click", function(event) {
				// 確保點擊的是背景遮罩，非表單本身
				if (event.target === document.getElementById("modalOverlay")) {
					closeResult();
				}
			});
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById("result").innerHTML = `<p>發生錯誤，請再試一次。</p>`;
    });
});