import requests

# 你的 iNaturalist API 金鑰 (可從官方申請)
ACCESS_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo5MDUyMDM0LCJleHAiOjE3NDMwMDQ1NTd9.CHS1Ma3maKkSikEzY7fJaYgU6bTF4JXANFsXY2uJ8D2n9Ff4kwvzyaLuUHihQCTu8W61Ey14MfevCgBcIqqWOg"

url = "https://api.inaturalist.org/v1/computervision/score_image"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

files = {'image': open('fish_photo.png', 'rb')}  # 確保圖片路徑正確
response = requests.post(url, headers=headers, files=files)

print("HTTP 狀態碼:", response.status_code)  # 先檢查 API 是否成功
# print("返回內容:", response.text)  # 檢查返回內容
data = response.json()
for result in data["results"]:
    taxon = result.get("taxon", {})
    if "preferred_common_name" in taxon:
        preferred_name = taxon["preferred_common_name"]
        break  # 找到第一個有名稱的就停止

try:
    
    if preferred_name:
        print(preferred_name)
    else:
        print("請再拍攝更清楚的照片哦~")
except requests.exceptions.JSONDecodeError:
    print("返回的內容不是 JSON，請檢查 API 是否正常")