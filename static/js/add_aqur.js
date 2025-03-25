document.getElementById("aquarium-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let form = document.getElementById("aquarium-form");
    let loadingMessage = document.getElementById("loading");
    let resultContainer = document.getElementById("result");

    // 顯示載入動畫
    form.classList.add("loading");

    // 取得表單資料
    const fishSpecies = document.getElementById("fish_species").value;
    const fishAmount = document.getElementById("fish_amount").value;

    // 發送 POST 請求到後端
    fetch('/get_aquarium_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fish_species: fishSpecies,
            fish_amount: parseInt(fishAmount)
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
function closeResult() {
        document.getElementById("result").style.display = "none";
		document.getElementById("modalOverlay").style.display = "none";
    }
document.getElementById("AI-check-form").addEventListener("submit", function(event) {
    event.preventDefault();

    // 收集所有資訊
    const aquariumName = document.getElementById("aquarium_name").value;
    const fishSpecies = document.getElementById("fish_species").value;
    const fishAmount = document.getElementById("fish_amount").value;
    const aiModel = document.getElementById("AI_model").value;
    const minTemp = document.getElementById("min_temp").value;
    const maxTemp = document.getElementById("max_temp").value;
    const feedingFrequency = document.getElementById("feeding_frequency").value;
    const feedingAmount = document.getElementById("feeding_amount").value;

    // 將資料發送到後端
    fetch("/add_aquarium", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            aquarium_name: aquariumName,
            fish_species: fishSpecies,
            fish_amount: fishAmount,
            AI_model: aiModel,
            min_temp: minTemp,
            max_temp: maxTemp,
            feeding_frequency: feedingFrequency,
            feeding_amount: feedingAmount
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === "success") {
            alert(result.message);
            window.location.href = "/user_console"; // 成功後返回主頁
        } else {
            alert(result.message);
        }
    })
    .catch(error => {
        alert("提交失敗，請稍後再試！");
    });
});

