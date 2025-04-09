fetch('/api/profile')
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            document.getElementById("username").innerText = data.name;
            document.getElementById("user-email").innerText = data.email;
            document.getElementById("user-avatar").src = data.picture;

            console.log("使用者語言: " + data.locale);
            console.log("Google ID: " + data.google_id);
        }
    })
    .catch(error => {
        console.log("發生錯誤:", error);
    });
	
	function toggleSubMenu() {
        var menu = document.getElementById("colorModeMenu");
        menu.style.display = (menu.style.display === "none" || menu.style.display === "") ? "block" : "none";
    }
	
	// 切換為淺色模式
	function changeToLightMode() {
		document.body.classList.remove('dark-mode');
		document.body.classList.add('light-mode');
	}
	// 切換為深色模式
	function changeToDarkMode() {
		document.body.classList.remove('light-mode');
		document.body.classList.add('dark-mode');
	}