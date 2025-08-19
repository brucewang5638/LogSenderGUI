# app/app_controller.py
import customtkinter
import tkinter
from tkinter import filedialog
import os
import time
import threading

import config
from app.ui_builder import create_widgets
from app.log_service import LogService

class AppController(customtkinter.CTk):
    """
    主控制器类，负责：
    1. 初始化UI和业务逻辑服务。
    2. 管理UI状态（通过StringVar）。
    3. 提供UI事件的回调方法，并将业务逻辑委托给LogService。
    """
    def __init__(self):
        super().__init__()

        # ---- Window and Theme ----
        self.title("日志发送工具 (Refactored)")
        self.geometry("800x600")
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        # ---- Data Variables for UI ----
        self.source_dir = tkinter.StringVar()
        self.processed_dir = tkinter.StringVar()
        self.udp_ip = tkinter.StringVar(value=config.DEFAULT_UDP_IP)
        self.udp_port = tkinter.StringVar(value=config.DEFAULT_UDP_PORT)
        self.http_url = tkinter.StringVar(value=config.DEFAULT_HTTP_URL)

        # ---- Service Layer ----
        self.log_service = LogService(
            config=self.get_current_config(),
            logger_callback=self.log_from_thread,
            on_stop_callback=self.on_processing_stopped
        )

        # ---- UI Creation ----
        # create_widgets needs access to self to bind commands and variables
        create_widgets(self)

    def get_current_config(self):
        return {
            'udp_ip': self.udp_ip.get(),
            'udp_port': self.udp_port.get(),
            'http_url': self.http_url.get()
        }

    def log_from_thread(self, message):
        """A thread-safe method to log messages from other threads."""
        self.after(0, self.log, message)

    def log(self, message):
        """Logs a message to the textbox, must be called from the main thread."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tkinter.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see(tkinter.END)

    def browse_source_dir(self):
        dir_path = filedialog.askdirectory(title="选择原始日志目录")
        if dir_path:
            self.source_dir.set(dir_path)
            self.log(f"设置原始日志目录为: {dir_path}")
            processed_dir_path = dir_path + "_processed"
            try:
                os.makedirs(processed_dir_path, exist_ok=True)
                self.processed_dir.set(processed_dir_path)
                self.log(f"自动设置已处理目录为: {processed_dir_path}")
            except OSError as e:
                self.log(f"错误: 创建已处理目录失败: {e}")

    def browse_processed_dir(self):
        dir_path = filedialog.askdirectory(title="选择已处理日志存放目录")
        if dir_path:
            self.processed_dir.set(dir_path)
            self.log(f"设置已处理目录为: {dir_path}")

    def start_processing(self):
        source = self.source_dir.get()
        processed = self.processed_dir.get()
        if not source or not processed:
            self.log("错误: '原始日志目录' 和 '已处理目录' 不能为空。")
            return
        
        self.log_service.config = self.get_current_config()
        if self.log_service.start_processing(source, processed):
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")

    def stop_processing(self):
        self.log_service.stop_processing()

    def on_processing_stopped(self):
        self.log_from_thread("处理服务已停止。" )
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def test_send_all(self):
        self.test_button.configure(state="disabled")
        self.log("--- 开始统一测试发送(后台) ---")
        test_thread = threading.Thread(target=self._test_send_thread_target, daemon=True)
        test_thread.start()

    def _test_send_thread_target(self):
        self.log_service.config = self.get_current_config()
        self.log_service.test_send(self.get_test_data())
        self.after(0, self._on_test_finished)

    def _on_test_finished(self):
        self.log("--- 统一测试发送结束 ---")
        self.test_button.configure(state="normal")

    def get_test_data(self):
        return [
            {
                "agent": "Mozilla/5.0 (Windows NT 6.1; WW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                "app_protocol": 1, "content_disposition": "inline", "content_length": 1375, "content_range": "bytes 5000-10000",
                "content_type": "file", "cookie": "-36", "data_type": 2, "device_id": "800020003006494",
                "device_ip": "127.0.0.1", "device_port_id": 2, "dip": "192.168.1.1", "dipv6": "",
                "dmac": "00:50:56:22:F1:1A", "dport": 80, "host": "192.168.1.1", "http_req_header": "GET//",
                "http_res_code": 200, "http_res_header": "200 OK", "interface_icon": "核心交换", "log_type": 3,
                "method": "GET", "network_protocol": 0, "origin": None, "referer": "http://192.168.1.1/",
                "sess_id": "19dbcd23-ef67-11ef-891d-6c92bfb82922", "session_protocol": -99, "setcookie": None,
                "sip": "192.168.0.1", "sipv6": "", "smac": "00:50:56:22:7D:8E", "sport": 53202,
                "time": 1740041119397, "transport_protocol": 6, "uri": "/login1", "xff": "10.95.58.130"
            },
            {
                "action_type": "主机在线信息上报", "behaviour_type": "一般行为", "company": "测试公司",
                "critical_level": "信息", "handle": "审计",
                "host_info_list": [
                    {"host_ip": "192.168.0.101", "is_online": "0", "mac": "00:50:56:22:7D:8A"},
                    {"host_ip": "192.168.0.102", "is_online": "1", "mac": "00:50:56:22:7D:8E"}
                ],
                "log_time": "2025-01-01 16:45:55", "log_type": "在线主机列表日志", "product": "主机监控与审计系统",
                "result": "成功", "send_time": "2025-01-01 16:45:55"
            }
        ]
