import tkinter as tk
from PIL import Image, ImageTk
import requests
import ctypes
from io import BytesIO
import time


def hijack_window_to_desktop(root_window):
    user32 = ctypes.windll.user32
    
    progman = user32.FindWindowW("Progman", None)
    
    user32.SendMessageW(progman, 0x052C, 0, 0)
    time.sleep(10)  # 等待 Windows 處理訊息
    
    workerw = None
    def enum_windows_proc(hwnd, lParam):
        nonlocal workerw
        p = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if p != 0:
            workerw = user32.FindWindowExW(0, hwnd, "WorkerW", None)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)

    if workerw:
        my_hwnd = user32.FindWindowW(None, root_window.title())
        user32.SetParent(my_hwnd, workerw)
        print(f"success！ (Parent HWND: {workerw})")
    else:
        print("Error: WorkerW not found")

def main():
    image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSP9s0mqOGimlo1Y0GvMJVihWoC7Xf4hfxg_w&s"

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_data = BytesIO(response.content)
        
        root = tk.Tk()
        root.title("NASA_Wallpaper_Overlay")
        
        root.overrideredirect(True)
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        pil_img = Image.open(img_data)
        pil_img = pil_img.resize((screen_width, screen_height), Image.ANTIALIAS)
        tk_img = ImageTk.PhotoImage(pil_img)
        
        label = tk.Label(root, image=tk_img)
        label.pack(fill="both", expand=True)
        
        root.update()
        
        hijack_window_to_desktop(root)
        
        root.mainloop()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()