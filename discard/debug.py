import ctypes
import time

user32 = ctypes.windll.user32

# 定義 Callback 函數類型
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def find_desktop_structure():
    print("--- 開始掃描桌面視窗結構 ---")
    
    # 1. 先找 Progman
    progman = user32.FindWindowW("Progman", None)
    print(f"[1] Progman (原始桌面) Handle: {progman}")

    # 2. 嘗試發送訊息 (多試幾次，有時候 Windows 需要被叫醒)
    print("正在發送 0x052C 訊息給 Progman...")
    result = ctypes.c_void_p()
    user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0x0002, 1000, ctypes.byref(result))
    
    # 給 Windows 一點時間反應
    time.sleep(1) 

    # 3. 遍歷所有視窗找出圖示層在哪
    print("\n[2] 尋找 SHELLDLL_DefView (圖示層)...")
    
    icon_parent = None
    target_workerw = None

    def enum_windows_callback(hwnd, lParam):
        nonlocal icon_parent, target_workerw
        
        # 取得類別名稱
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)
        name = class_name.value

        # 如果這個視窗裡面有圖示層 (SHELLDLL_DefView)
        def_view = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        
        if def_view:
            icon_parent = hwnd
            print(f"✅ 找到圖示層! 它的父視窗是: {name} (Handle: {hwnd})")
            
            # 如果父視窗已經是 WorkerW，那我們要找的就是「下一個」WorkerW
            if name == "WorkerW":
                # 找這個視窗的兄弟
                target_workerw = user32.FindWindowExW(0, hwnd, "WorkerW", None)
                print(f"   -> 鎖定目標: 應該是它的兄弟 WorkerW (Handle: {target_workerw})")
            return False # 停止掃描
        
        return True # 繼續找

    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

    print("\n--- 診斷結果 ---")
    if icon_parent:
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(icon_parent, class_name, 256)
        if class_name.value == "Progman":
            print("❌ 失敗：圖示層還黏在 Progman 上。")
            print("原因可能：你的桌面背景設定是「純色 (Solid Color)」嗎？")
            print("解決：請換成一張圖片當桌布，然後再試一次。")
        elif target_workerw:
             print(f"✅ 成功：可以劫持的目標視窗是 {target_workerw}")
        else:
            print("⚠️ 奇怪：圖示層在 WorkerW 裡，但找不到它的兄弟視窗。")
    else:
        print("❌ 嚴重錯誤：完全找不到圖示層 (SHELLDLL_DefView)。")

if __name__ == '__main__':
    find_desktop_structure()