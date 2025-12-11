import tkinter as tk
from PIL import Image, ImageTk
import requests
import ctypes
from io import BytesIO
import time

# 這裡 import 你原本的檔案 (假設檔名是 nasa_api.py)
# 這樣就可以直接用你原本寫好的 get_nasa_apod 功能
import discard.NASAapi as nasa_api

def hijack_window_to_desktop(root_window):
    """
    這段是 Windows API 的黑魔法。
    它會尋找桌面圖示後面的那一層 (WorkerW)，
    然後把我們的視窗「黏」上去。
    """
    user32 = ctypes.windll.user32
    
    # 1. 找到 Program Manager 視窗
    progman = user32.FindWindowW("Progman", None)
    
    # 2. 發送 0x052C 訊息，觸發 Windows 生成 WorkerW 分層
    user32.SendMessageW(progman, 0x052C, 0, 0)
    time.sleep(10)  # 等待 Windows 處理訊息
    
    # 3. 尋找剛剛生成的 WorkerW (位於圖示下方)
    workerw = None
    def enum_windows_proc(hwnd, lParam):
        nonlocal workerw
        p = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if p != 0:
            # 找到圖示層的兄弟，就是我們要的背景層
            workerw = user32.FindWindowExW(0, hwnd, "WorkerW", None)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)

    if workerw:
        # 4. 設定父視窗：將我們的視窗設為 WorkerW 的子視窗
        # 為了保險，我們先用視窗標題抓取我們的視窗 Handle
        my_hwnd = user32.FindWindowW(None, root_window.title())
        user32.SetParent(my_hwnd, workerw)
        print(f"成功將視窗嵌入桌面！ (Parent HWND: {workerw})")
    else:
        print("失敗：找不到 WorkerW")

def main():
    print("正在呼叫 nasa_api 取得資料...")
    
    # --- 關鍵點：使用你原本檔案裡的功能 ---
    #data = nasa_api.get_nasa_apod()
    
    #if not data:
    #    print("無法取得 NASA 資料，程式結束。")
    #    return

    image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSP9s0mqOGimlo1Y0GvMJVihWoC7Xf4hfxg_w&s"#data['image_url']
    print(f"取得圖片 URL: {image_url}")
    print("下載圖片並準備顯示...")

    try:
        # 根據 URL 下載圖片數據
        response = requests.get(image_url)
        response.raise_for_status()
        img_data = BytesIO(response.content) # 轉成記憶體內的二進位檔
        
        # --- 建立 GUI 介面 ---
        root = tk.Tk()
        root.title("NASA_Wallpaper_Overlay") # 設定標題以便搜尋
        
        # 移除標題列與邊框
        root.overrideredirect(True)
        
        # 取得螢幕解析度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 設定視窗大小與位置
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 處理圖片 (縮放以填滿螢幕)
        pil_img = Image.open(img_data)
        pil_img = pil_img.resize((screen_width, screen_height), Image.ANTIALIAS)
        tk_img = ImageTk.PhotoImage(pil_img)
        
        # 顯示圖片
        label = tk.Label(root, image=tk_img)
        label.pack(fill="both", expand=True)
        
        # 強制更新一次介面以確保視窗生成
        root.update()
        
        # 執行劫持
        hijack_window_to_desktop(root)
        
        print("桌布設定完成！請看桌面。")
        print("若要關閉，請回到此終端機按 Ctrl+C")
        
        root.mainloop()

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()