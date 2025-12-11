import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

# --- Windows API 定義 (與作業系統溝通的橋樑) ---
user32 = ctypes.windll.user32

# 定義我們需要的 C 語言結構與函數
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def get_wallpaper_workerw():
    """
    這個函數負責找到那個神秘的 'WorkerW' 視窗控制代碼 (Handle)。
    """
    # 1. 找到 Progman (原本的桌面視窗)
    progman = user32.FindWindowW("Progman", None)

    # 2. 發送魔法訊息 0x052C
    # 這會觸發 Windows 建立一個新的 WorkerW 視窗在圖示層後面
    result = ctypes.c_void_p()
    user32.SendMessageTimeoutW(
        progman,
        0x052C,
        0,
        0,
        0x0002, # SMTO_NORMAL
        1000,
        ctypes.byref(result)
    )

    # 3. 尋找正確的 WorkerW
    # 邏輯：我們要找的 WorkerW，是「含有 SHELLDLL_DefView 的那個視窗」的「下一個兄弟視窗」
    workerw = None

    def enum_windows_callback(hwnd, lParam):
        nonlocal workerw
        # 檢查這個視窗底下有沒有 SHELLDLL_DefView (桌面圖示層)
        shell_dll = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        
        if shell_dll:
            # 如果找到了圖示層，那麼它的「下一個兄弟 WorkerW」就是我們要找的背景層
            workerw = user32.FindWindowExW(0, hwnd, "WorkerW", None)
            return False # 找到了，停止搜尋
        return True # 繼續找

    # 開始遍歷所有視窗
    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    
    return workerw

# --- PyQt6 視窗定義 (我們未來的畫布) ---
class DesktopWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 設定視窗標題
        self.setWindowTitle('Cosmic Pulse - Step 1')
        
        # 設定背景顏色 (這裡用深藍色模擬太空)
        self.setStyleSheet("background-color: #0B0B3B;") 
        
        # 加入一段測試文字
        layout = QVBoxLayout()
        label = QLabel("Hello, Cosmic Pulse!", self)
        label.setStyleSheet("color: white; font-size: 40px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # 加入說明文字
        sub_label = QLabel("按 'ESC' 鍵關閉此程式", self)
        sub_label.setStyleSheet("color: #AAAAAA; font-size: 20px;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_label)
        
        self.setLayout(layout)
        
        # 設定視窗為無邊框 (看起來才像桌布)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 先設定一個初始大小 (全螢幕)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen_geometry.width(), screen_geometry.height())

    def keyPressEvent(self, event):
        # 因為視窗在圖示下面，滑鼠可能點不到關閉按鈕，所以設定 ESC 鍵退出
        if event.key() == Qt.Key.Key_Escape:
            self.close()

# --- 主程式 ---
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 1. 取得背景層的 Handle
    wallpaper_hwnd = get_wallpaper_workerw()
    
    if not wallpaper_hwnd:
        print("錯誤：找不到 WorkerW，視窗劫持失敗。")
        sys.exit(1)
    
    print(f"成功找到背景層 HWND: {wallpaper_hwnd}")

    # 2. 建立我們的 PyQt 視窗
    window = DesktopWindow()
    window.show() # 先顯示出來，這時候它還是一個普通視窗，會蓋住圖示
    
    # 3. 【關鍵時刻】把我們的視窗黏到背景層上
    # 取得 PyQt 視窗的 Handle (必須轉成 int)
    my_window_hwnd = int(window.winId())
    
    # 設定父視窗為 WorkerW
    user32.SetParent(my_window_hwnd, wallpaper_hwnd)
    
    print("視窗已嵌入桌面層！請看你的桌面背景。")
    print("按 ESC 鍵可關閉程式。")

    sys.exit(app.exec())