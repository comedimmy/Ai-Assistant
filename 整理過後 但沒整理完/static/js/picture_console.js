    function fetchPhotos() {
        const aquariumId = document.getElementById("aquarium_id").value;
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
                    const img = document.createElement("img");
                    img.src = photo.URL.replace(/\\/g, "/"); // 修正可能的反斜槓問題
                    img.alt = "水族箱照片";
                    img.style.width = "300px";
                    img.style.margin = "10px";
                    container.appendChild(img);
                });
            })
            .catch(error => console.error("查詢失敗:", error));
    }