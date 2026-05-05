import cloudscraper
from bs4 import BeautifulSoup
import time
import random

def get_chapter_list(scraper, index_url):
    """從目錄頁抓取所有章節的完整網址"""
    print("正在讀取目錄，請稍候...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': 'https://www.oop.tw/'
    }
    try:
        response = scraper.get(index_url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        # 該網站的目錄通常放在 <div id="list"> 裡面的 <dd> 標籤
        list_box = soup.find('div', id='list')
        if not list_box:
            # 如果找不到 id='list'，就抓取頁面所有 <a>
            list_box = soup

        for a in list_box.find_all('a', href=True):
            href = a['href']
            # 觀察該網站連結格式通常為 'a' + 數字 + 'a.html'
            # 例如: a2147072a.html
            if 'html' in href and '_' not in href:
                # 提取中間的數字 ID
                # 這裡改為提取檔名，不純抓數字，避免 ID 前後的 'a' 影響
                parts = href.split('/')[-1].replace('.html', '')
                # 移除頭尾可能存在的 'a'
                c_id = parts.strip('a')
                if c_id.isdigit():
                    links.append(c_id)
        
        # 去除重複項並保持順序
        unique_links = []
        for x in links:
            if x not in unique_links:
                unique_links.append(x)
                
        print(f"成功分析目錄！共找到 {len(unique_links)} 個章節。")
        return unique_links
    except Exception as e:
        print(f"讀取目錄失敗: {e}")
        return []

def fetch_content(scraper, url):
    """抓取內文邏輯"""
    try:
        response = scraper.get(url, timeout=15)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            article = soup.find(id='article')
            if article:
                for s in article(['script', 'style', 'div']): s.decompose()
                return article.get_text(separator='\n', strip=True)
    except:
        pass
    return ""

def main():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    
    index_url = "https://www.oop.tw/abooka/a31537152a/"
    chapter_ids = get_chapter_list(scraper, index_url)
    
    if not chapter_ids:
        print("未找到任何章節，請檢查目錄網址。")
        return

    # 設定爬取範圍 (例如從第 1 章爬到第 10 章)
    start_at = 0 
    end_at = 10 
    chapters_to_crawl = chapter_ids[start_at:end_at]
    
    all_content = []
    save_count = 5 # 每 5 章存一檔

    for i, c_id in enumerate(chapters_to_crawl):
        real_index = start_at + i + 1
        print(f"進度: {real_index}/{len(chapter_ids)} - 正在爬取 ID: {c_id}")
        
        # 組合第一頁與第二頁網址
        p1 = f"https://www.oop.tw/areada/a31537152a/a{c_id}a.html"
        p2 = f"https://www.oop.tw/areada/a31537152a/a{c_id}_2a.html"
        
        text1 = fetch_content(scraper, p1)
        time.sleep(random.uniform(1, 2))
        text2 = fetch_content(scraper, p2)
        
        combined = f"\n\n### 第 {real_index} 章 (ID: {c_id}) ###\n\n{text1}\n{text2}\n"
        all_content.append(combined)
        
        # 每 5 章存檔
        if len(all_content) == save_count:
            file_name = f"novel_part_{real_index // save_count}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.writelines(all_content)
            print(f"==> 已儲存: {file_name}")
            all_content = []
            
        time.sleep(random.uniform(2, 4))

    # 處理剩餘章節
    if all_content:
        with open("novel_part_final.txt", "w", encoding="utf-8") as f:
            f.writelines(all_content)
        print("==> 剩餘章節已儲存。")

if __name__ == "__main__":
    main()