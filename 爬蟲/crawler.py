import requests
from bs4 import BeautifulSoup
import time
import os

def get_content(url):
    """取得特定網址中 id='article' 的文字內容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # 若出現亂碼，請嘗試改為 'gbk'
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find(id='article')
        if article:
            # 移除不必要的標籤（如廣告、腳本）
            for s in article(['script', 'style']):
                s.decompose()
            return article.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"爬取 {url} 時發生錯誤: {e}")
    return ""

def main():
    # 基礎 URL 設定
    base_url = "https://www.oop.tw/areada/a31537152a/a{}.html"
    start_id = 2147072  # 起始章節 ID
    total_chapters = 20 # 你想爬取的總章節數
    chapters_per_file = 5
    
    current_batch_content = []
    
    for i in range(total_chapters):
        curr_id = start_id + i
        print(f"正在爬取第 {i+1} 章 (ID: {curr_id})...")
        
        # 第一頁與第二頁網址
        page1_url = base_url.format(curr_id)
        page2_url = base_url.format(f"{curr_id}_2")
        
        # 合併兩頁內容
        content1 = get_content(page1_url)
        content2 = get_content(page2_url)
        full_chapter = f"--- 第 {i+1} 章 (ID: {curr_id}) ---\n{content1}\n{content2}\n\n"
        
        current_batch_content.append(full_chapter)
        
        # 每 5 章輸出一個檔案
        if (i + 1) % chapters_per_file == 0:
            file_index = (i + 1) // chapters_per_file
            filename = f"novel_part_{file_index}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(current_batch_content)
            print(f"已儲存檔案: {filename}")
            current_batch_content = [] # 清空緩存
        
        # 禮貌爬蟲：避免請求過快被封鎖
        time.sleep(1)

if __name__ == "__main__":
    main()