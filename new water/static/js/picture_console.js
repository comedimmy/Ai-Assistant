function fetchPhotos() {
    const urlParams = new URLSearchParams(window.location.search);
    const aquariumId = urlParams.get('aquarium_id');  

    if (!aquariumId) {
        alert("請輸入水族箱 ID");
        return;
    }

    fetch(`/api/get_photos?aquarium_id=${aquariumId}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("photo-container");
            container.innerHTML = ""; // 清空舊內容

            if (data.length === 0) {
                container.innerHTML = "<p>沒有找到照片</p>";
                return;
            }

            data.forEach(photo => {
                const photoDiv = document.createElement("div");
                const img = document.createElement("img");
                img.alt = "水族箱照片";
                img.src = photo.path;  // 假設圖片 URL 存在於 `path` 欄位
                img.style.width = "300px";
                img.style.margin = "10px";
                };
            });
        })
        .catch(error => console.error("查詢失敗:", error));
}

function deletePhoto(photoPath) {
    const urlParams = new URLSearchParams(window.location.search);
    const aquariumId = urlParams.get('aquarium_id');  

    if (!aquariumId) {
        alert("請輸入水族箱 ID");
        return;
    }

    fetch(`/api/delete_photo?aquarium_id=${aquariumId}&photo_path=${encodeURIComponent(photoPath)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("照片已刪除");
            fetchPhotos();  // 更新顯示
        } else {
            alert("刪除失敗");
        }
    })
    .catch(error => console.error("刪除失敗:", error));
}
