function sendData() {
	let inputText = document.getElementById("userInput").value;

	// 將資料打包成JSON
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
		// 創建一個新的<div>元素並將資料顯示在其中
		const displayElement = document.createElement('div');
		displayElement.textContent = "回應：" + JSON.stringify(data);
		document.body.appendChild(displayElement); // 將<div>加入到body中
	})
	.catch(error => console.error("錯誤:", error));
}
function typeWriterEffect(text, elementId, speed = 50) {
	let index = 0;
	const element = document.getElementById(elementId);
	element.textContent = ""; // 清空內容

	function type() {
		if (index < text.length) {
			element.textContent += text.charAt(index);
			index++;
			setTimeout(type, speed);
		}
	}
	type();
}
	   
window.onload = function() {
	setTimeout(() => {
		typeWriterEffect("你想問些甚麼嗎?", "title", 80);
	}, 1000); 
};
function sendQuation() {
	let inputText = document.getElementById("userInputQuation").value;

	
	let existingElement = document.getElementById("typing-effect");
	if (existingElement) {
		existingElement.remove();
	}

	
	const displayElement = document.createElement('div');
	displayElement.id = "typing-effect";
	displayElement.textContent = "思考中"; // 初始文字
	document.body.appendChild(displayElement);

	
	let dots = 0;
	const loadingInterval = setInterval(() => {
		if (dots < 3) {
			displayElement.textContent += ".";
			dots++;
		} else {
			displayElement.textContent = "思考中"; // 重置
			dots = 0;
		}
	}, 1000); // 每秒更新一次

	// 將資料打包成JSON
	let jsonData = {
		"message": inputText
	};

	fetch("http://127.0.0.1:5000/receive", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify(jsonData)
	})
	.then(response => response.json())
	.then(data => {
		clearInterval(loadingInterval); 
		displayElement.textContent = ""; // 清空顯示區域
		typeWriterEffect(data.result, "typing-effect", 50); 
	})
	.catch(error => {
		clearInterval(loadingInterval); 
		displayElement.textContent = "發生錯誤，請稍後再試！"; 
		console.error("錯誤:", error);
	});
}