from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random

def get_chapter_ids_with_selenium(index_url):
    """使用 Selenium 模擬瀏覽器點擊目錄分頁"""
    chrome_options = Options()
    # 如果想看瀏覽器跑，註解掉下面這行；如果不想看視窗，就留著
    # chrome_options.add_argument("--headless") 
    
    driver = webdriver.Chrome(options=chrome_options)
    all_chapter_ids = []
    
    try:
        driver.get(index_url)
        print("請注意：如果出現機器人驗證，請手動在瀏覽器視窗點選驗證...")
        
        # 等待目錄區塊載入
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "tab-catalog")))

        # 找到所有的 cp-btn (目錄分頁按鈕)
        btns = driver.find_elements(By.CLASS_NAME, "cp-btn")
        btn_count = len(btns) if btns else 1
        print(f"發現 {btn_count} 個目錄分頁按鈕。")

        for i in range(btn_count):
            print(f"正在讀取第 {i+1} 個分頁...")
            
            # 重新獲取按鈕以避免頁面更新導致的失效
            current_btns = driver.find_elements(By.CLASS_NAME, "cp-btn")
            if current_btns:
                # 捲動到按鈕位置並點擊
                driver.execute_script("arguments[0].scrollIntoView();", current_btns[i])
                time.sleep(1)
                driver.execute_script("arguments[0].click();", current_btns[i])
                time.sleep(3) # 等待內容異步載入

            # 抓取當前頁面的 HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            catalog_box = soup.find(id='tab-catalog')
            
            if catalog_box:
                for a in catalog_box.find_all('a', href=True):
                    href = a['href']
                    if 'html' in href and '_' not in href:
                        c_id = href.split('/')[-1].replace('.html', '').strip('a')
                        if c_id.isdigit() and c_id not in all_chapter_ids:
                            all_chapter_ids.append(c_id)
        
        print(f"成功依序抓取 {len(all_chapter_ids)} 個章節 ID。")
        return all_chapter_ids

    except Exception as e:
        print(f"Selenium 執行錯誤: {e}")
        return []
    finally:
        driver.quit()

# 這裡共用先前的 fetch_content 函數，但改用 cloudscraper 抓內文以節省效能
import cloudscraper
def fetch_content(scraper, url):
    try:
        res = scraper.get(url, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        article = soup.find(id='article')
        if article:
            for s in article(['script', 'style', 'div']): s.decompose()
            return article.get_text(separator='\n', strip=True)
    except: pass
    return ""

def main():
    index_url = "https://www.oop.tw/abooka/a31537152a/"
    
    # 1. 先用 Selenium 拿目錄
    chapter_ids = get_chapter_ids_with_selenium(index_url)
    
    if not chapter_ids:
        print("終止程式：無法取得目錄。")
        return

    # 2. 開始爬內容
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','desktop': True})
    all_content = []
    
    for i, c_id in enumerate(chapter_ids):
        # 為了測試，你可以先爬前 5 章試試看
        if i >= 10: break 
        
        print(f"[{i+1}/{len(chapter_ids)}] 抓取中: {c_id}")
        p1 = f"https://www.oop.tw/areada/a31537152a/a{c_id}a.html"
        p2 = f"https://www.oop.tw/areada/a31537152a/a{c_id}_2a.html"
        
        t1 = fetch_content(scraper, p1)
        time.sleep(1)
        t2 = fetch_content(scraper, p2)
        
        all_content.append(f"\n第 {i+1} 章\n{t1}\n{t2}\n")
        
        if len(all_content) == 5:
            with open(f"novel_{i//5}.txt", "w", encoding="utf-8") as f:
                f.writelines(all_content)
            all_content = []
        
        time.sleep(random.uniform(2, 4))

if __name__ == "__main__":
    main()
    