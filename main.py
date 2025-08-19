
import customtkinter
import tkinter
from tkinter import filedialog
import os
import json
import time
import threading
import socket
import requests

# 设置customtkinter的外观
customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ---- 窗口配置 ----
        self.title("日志发送工具")
        self.geometry("800x600")

        # ---- 主体网格布局 ----
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ---- 数据变量 ----
        self.source_dir = tkinter.StringVar()
        self.processed_dir = tkinter.StringVar()
        self.udp_ip = tkinter.StringVar(value="192.168.1.66")
        self.udp_port = tkinter.StringVar(value="19708")
        self.http_url = tkinter.StringVar(value="http://192.168.1.66:19762/V1/log")
        self.is_processing = False
        self.processing_thread = None

        # ---- 界面元素 ----
        self.create_widgets()

    def create_widgets(self):
        # ---- 目录选择区 ----
        dir_frame = customtkinter.CTkFrame(self)
        dir_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        dir_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(dir_frame, text="原始日志目录:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        source_entry = customtkinter.CTkEntry(dir_frame, textvariable=self.source_dir, state="readonly")
        source_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(dir_frame, text="浏览...", command=self.browse_source_dir).grid(row=0, column=2, padx=10, pady=5)

        customtkinter.CTkLabel(dir_frame, text="已处理目录:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        processed_entry = customtkinter.CTkEntry(dir_frame, textvariable=self.processed_dir, state="readonly")
        processed_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        customtkinter.CTkButton(dir_frame, text="浏览...", command=self.browse_processed_dir).grid(row=1, column=2, padx=10, pady=5)

        # ---- 服务配置区 ----
        service_frame = customtkinter.CTkFrame(self)
        service_frame.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
        service_frame.grid_columnconfigure(0, weight=1)
        service_frame.grid_columnconfigure(1, weight=1)

        # UDP 配置
        udp_frame = customtkinter.CTkFrame(service_frame)
        udp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        udp_frame.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(udp_frame, text="本地日志 (UDP)").grid(row=0, column=0, columnspan=3, padx=10, pady=5)

        customtkinter.CTkLabel(udp_frame, text="IP地址:").grid(row=1, column=0, padx=(10,0), pady=5, sticky="w")
        customtkinter.CTkEntry(udp_frame, textvariable=self.udp_ip).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkLabel(udp_frame, text="端口:").grid(row=2, column=0, padx=(10,0), pady=5, sticky="w")
        customtkinter.CTkEntry(udp_frame, textvariable=self.udp_port).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # HTTP 配置
        http_frame = customtkinter.CTkFrame(service_frame)
        http_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        http_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(http_frame, text="流量日志 (HTTP)").grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        customtkinter.CTkLabel(http_frame, text="URL:").grid(row=1, column=0, padx=(10,0), pady=5, sticky="w")
        customtkinter.CTkEntry(http_frame, textvariable=self.http_url, width=300).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # ---- 日志显示区 ----
        self.log_textbox = customtkinter.CTkTextbox(self, state="disabled")
        self.log_textbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # ---- 主控制区 ----
        control_frame = customtkinter.CTkFrame(self)
        control_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        self.test_button = customtkinter.CTkButton(control_frame, text="测试发送", command=self.test_send_all)
        self.test_button.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

        self.start_button = customtkinter.CTkButton(control_frame, text="开始处理", command=self.start_processing)
        self.start_button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.stop_button = customtkinter.CTkButton(control_frame, text="停止处理", command=self.stop_processing, state="disabled")
        self.stop_button.grid(row=1, column=1, padx=10, pady=(5, 10), sticky="ew")

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tkinter.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see(tkinter.END)

    def browse_source_dir(self):
        dir_path = filedialog.askdirectory(title="选择原始日志目录")
        if dir_path:
            self.source_dir.set(dir_path)
            self.log(f"设置原始日志目录为: {dir_path}")

            # ---- 新增逻辑：自动设置并创建已处理目录 ----
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

    def test_send_all(self):
        """
        当用户点击“测试发送”按钮时调用。
        此方法会禁用按钮并启动一个后台线程来执行实际的发送操作，以防止UI冻结。
        """
        self.test_button.configure(state="disabled")
        self.log("--- 开始统一测试发送(后台) ---")
        
        # 在后台线程中运行测试，以避免阻塞GUI
        test_thread = threading.Thread(target=self._test_send_thread_target, daemon=True)
        test_thread.start()

    def _test_send_thread_target(self):
        """
        这个函数在后台线程中执行，处理实际的测试日志发送。
        """
        test_data = self.get_test_data()

        # 注意：send_..._log方法是阻塞的，但因为它们在工作线程中被调用，所以不会冻z结UI
        self.send_http_log([test_data[0]])
        self.send_udp_log([test_data[1]])

        # 所有发送操作完成后，安排在主线程中执行收尾工作
        self.after(0, self._on_test_finished)

    def _on_test_finished(self):
        """
        测试完成后，在主GUI线程中调用此方法来更新UI。
        """
        self.log("--- 统一测试发送结束 ---")
        self.test_button.configure(state="normal")

    def send_udp_log(self, log_batch):
        log_count = len(log_batch)
        self.after(0, lambda: self.log(f"开始发送一批 {log_count} 条UDP日志..."))
        ip = self.udp_ip.get()
        port_str = self.udp_port.get()

        if not ip or not port_str:
            self.after(0, lambda: self.log("错误: UDP IP地址和端口不能为空。"))
            return

        try:
            port = int(port_str)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = json.dumps(log_batch, ensure_ascii=False).encode('utf-8')
            sock.sendto(message, (ip, port))
            self.after(0, lambda: self.log(f"成功发送一批 {log_count} 条UDP日志到 {ip}:{port}"))
        except ValueError:
            self.after(0, lambda: self.log(f"错误: 无效的UDP端口号 '{port_str}'"))
        except socket.error as e:
            self.after(0, lambda: self.log(f"错误: 发送UDP时发生套接字错误: {e}"))
        except Exception as e:
            self.after(0, lambda: self.log(f"错误: 发送UDP日志时发生未知异常: {e}"))

    def send_http_log(self, log_batch):
        log_count = len(log_batch)
        self.after(0, lambda: self.log(f"开始发送一批 {log_count} 条HTTP日志..."))
        url = self.http_url.get()
        if not url:
            self.after(0, lambda: self.log("错误: HTTP URL不能为空。"))
            return

        try:
            headers = {'Content-Type': 'application/json'}
            # 直接发送整个批处理列表
            response = requests.post(url, data=json.dumps(log_batch), headers=headers, timeout=10)
            self.after(0, lambda: self.log(f"HTTP响应状态码: {response.status_code}"))
            if response.status_code == 200:
                self.after(0, lambda: self.log(f"成功发送一批 {log_count} 条HTTP日志!"))
            else:
                self.after(0, lambda: self.log(f"错误: HTTP日志发送失败，状态码: {response.status_code}, 内容: {response.text}"))
        except requests.exceptions.RequestException as e:
            self.after(0, lambda: self.log(f"错误: 发送HTTP请求时发生异常: {e}"))

    def start_processing(self):
        source = self.source_dir.get()
        processed = self.processed_dir.get()

        if not source or not processed:
            self.log("错误: '原始日志目录' 和 '已处理目录' 不能为空。")
            return

        if not os.path.isdir(source) or not os.path.isdir(processed):
            self.log("错误: 指定的目录无效或不存在。")
            return

        self.is_processing = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.log("开始处理日志文件...")

        # 创建并启动后台处理线程
        self.processing_thread = threading.Thread(target=self._process_files_loop, daemon=True)
        self.processing_thread.start()

    def _process_files_loop(self):
        source_dir = self.source_dir.get()
        processed_dir = self.processed_dir.get()

        while self.is_processing:
            try:
                json_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.json')]
                if not json_files:
                    time.sleep(2)
                    continue

                for file_name in json_files:
                    if not self.is_processing: break
                    file_path = os.path.join(source_dir, file_name)
                    self.after(0, lambda f=file_name: self.log(f"正在处理文件: {f}"))

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)

                        if not isinstance(log_data, list):
                            self.after(0, lambda f=file_name: self.log(f"错误: {f} 的内容不是一个有效的JSON数组。"))
                            os.rename(file_path, os.path.join(processed_dir, file_name))
                            continue

                        # ---- 批处理逻辑 ----
                        http_batch = []
                        udp_batch = []
                        for log_entry in log_data:
                            if isinstance(log_entry.get('log_type'), int) and 'action_type' not in log_entry:
                                http_batch.append(log_entry)
                            else:
                                udp_batch.append(log_entry)
                        
                        # 发送HTTP批次
                        if http_batch:
                            if not self.is_processing: break
                            self.send_http_log(http_batch)
                        
                        # 发送UDP批次
                        if udp_batch:
                            if not self.is_processing: break
                            self.send_udp_log(udp_batch)
                        # ---- 批处理逻辑结束 ----

                        if not self.is_processing: break

                        processed_file_path = os.path.join(processed_dir, file_name)
                        os.rename(file_path, processed_file_path)
                        self.after(0, lambda f=file_name: self.log(f"文件 {f} 处理完成并已移动。"))

                    except json.JSONDecodeError:
                        self.after(0, lambda f=file_name: self.log(f"错误: {f} JSON格式无效。"))
                        os.rename(file_path, os.path.join(processed_dir, file_name))
                    except Exception as e:
                        self.after(0, lambda f=file_name, err=e: self.log(f"处理文件 {f} 时发生未知错误: {err}"))
                if not self.is_processing: break
            except Exception as e:
                self.after(0, lambda err=e: self.log(f"扫描目录时发生错误: {err}"))
            
            time.sleep(1)

        self.after(0, self.update_ui_on_stop)

    def stop_processing(self):
        if self.is_processing:
            self.log("正在请求停止处理...")
            self.is_processing = False
            # UI更新将由处理循环结束时触发

    def update_ui_on_stop(self):
        """在主线程中更新UI以反映停止状态"""
        self.log("处理已停止。")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
