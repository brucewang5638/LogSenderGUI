# main.py
# 主程序入口
from app.app_controller import AppController

if __name__ == "__main__":
    app = AppController()
    app.mainloop()