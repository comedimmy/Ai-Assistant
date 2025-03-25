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
window.onload = function() {
    // 發送 GET 請求，獲取水族箱詳細資訊
    fetch(`/aquarium_details/${aquariumId}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);  // 打印該水族箱的詳細資訊
        })
        .catch(error => {
            console.error('獲取水族箱詳細資訊失敗:', error);
        });
		
});