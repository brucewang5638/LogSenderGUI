# app/log_service.py
import os
import json
import time
import threading
import socket
import requests

class LogService:
    """
    处理所有核心业务逻辑：文件处理、日志发送等。
    独立于UI，通过回调函数与主应用通信。
    """
    def __init__(self, config, logger_callback, on_stop_callback):
        self.config = config
        self.log = logger_callback
        self.on_stop_callback = on_stop_callback
        self.is_processing = False
        self.processing_thread = None

    def start_processing(self, source_dir, processed_dir):
        if not os.path.isdir(source_dir) or not os.path.isdir(processed_dir):
            self.log("错误: 指定的目录无效或不存在。")
            return False

        self.is_processing = True
        self.log("后台处理服务已启动...")
        self.processing_thread = threading.Thread(
            target=self._process_files_loop,
            args=(source_dir, processed_dir),
            daemon=True
        )
        self.processing_thread.start()
        return True

    def stop_processing(self):
        if self.is_processing:
            self.log("正在请求停止处理...")
            self.is_processing = False

    def _process_files_loop(self, source_dir, processed_dir):
        while self.is_processing:
            try:
                json_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.json')]
                if not json_files:
                    time.sleep(2)
                    continue

                for file_name in json_files:
                    if not self.is_processing: break
                    file_path = os.path.join(source_dir, file_name)
                    self.log(f"正在处理文件: {file_name}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                        if not isinstance(log_data, list):
                            self.log(f"错误: {file_name} 的内容不是一个有效的JSON数组。")
                            os.rename(file_path, os.path.join(processed_dir, file_name))
                            continue
                        
                        http_batch, udp_batch = [], []
                        for log_entry in log_data:
                            if isinstance(log_entry.get('log_type'), int) and 'action_type' not in log_entry:
                                http_batch.append(log_entry)
                            else:
                                udp_batch.append(log_entry)
                        
                        if http_batch:
                            if not self.is_processing: break
                            self.send_http_log(http_batch)
                        if udp_batch:
                            if not self.is_processing: break
                            self.send_udp_log(udp_batch)
                        
                        if not self.is_processing: break
                        
                        processed_file_path = os.path.join(processed_dir, file_name)
                        if os.path.exists(processed_file_path):
                            os.remove(processed_file_path)
                            self.log(f"警告: 目标文件 {file_name} 已存在，已覆盖。")
                        os.rename(file_path, processed_file_path)
                        self.log(f"文件 {file_name} 处理完成并已移动。")
                    except json.JSONDecodeError:
                        self.log(f"错误: {file_name} JSON格式无效。")
                        os.rename(file_path, os.path.join(processed_dir, file_name))
                    except Exception as e:
                        self.log(f"处理文件 {file_name} 时发生未知错误: {e}")
                if not self.is_processing: break
            except Exception as e:
                self.log(f"扫描目录时发生错误: {e}")
            time.sleep(1)
        
        self.on_stop_callback()

    def send_udp_log(self, log_batch):
        log_count = len(log_batch)
        self.log(f"发送一批 {log_count} 条UDP日志...")
        ip = self.config['udp_ip']
        port_str = self.config['udp_port']
        try:
            port = int(port_str)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = json.dumps(log_batch, ensure_ascii=False).encode('utf-8')
            sock.sendto(message, (ip, port))
            self.log(f"成功发送UDP日志到 {ip}:{port}")
        except Exception as e:
            self.log(f"错误: 发送UDP日志时发生异常: {e}")

    def send_http_log(self, log_batch):
        log_count = len(log_batch)
        self.log(f"发送一批 {log_count} 条HTTP日志...")
        url = self.config['http_url']
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(log_batch), headers=headers, timeout=10)
            self.log(f"HTTP响应状态码: {response.status_code}")
            if response.status_code != 200:
                self.log(f"错误: HTTP日志发送失败，内容: {response.text}")
        except Exception as e:
            self.log(f"错误: 发送HTTP请求时发生异常: {e}")

    def test_send(self, test_data):
        self.log("发送HTTP测试日志...")
        self.send_http_log([test_data[0]])
        self.log("发送UDP测试日志...")
        self.send_udp_log([test_data[1]])
