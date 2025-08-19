# app/ui_builder.py
import customtkinter

def create_widgets(controller):
    """
    创建并布局所有UI组件。
    将所有组件的事件(command)绑定到controller实例的方法上。
    """
    # ---- 主体网格布局 ----
    controller.grid_columnconfigure(0, weight=1)
    controller.grid_rowconfigure(2, weight=1)

    # ---- 目录选择区 ----
    dir_frame = customtkinter.CTkFrame(controller)
    dir_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    dir_frame.grid_columnconfigure(1, weight=1)

    customtkinter.CTkLabel(dir_frame, text="原始日志目录:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    source_entry = customtkinter.CTkEntry(dir_frame, textvariable=controller.source_dir, state="readonly")
    source_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    customtkinter.CTkButton(dir_frame, text="浏览...", command=controller.browse_source_dir).grid(row=0, column=2, padx=10, pady=5)

    customtkinter.CTkLabel(dir_frame, text="已处理目录:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    processed_entry = customtkinter.CTkEntry(dir_frame, textvariable=controller.processed_dir, state="readonly")
    processed_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    customtkinter.CTkButton(dir_frame, text="浏览...", command=controller.browse_processed_dir).grid(row=1, column=2, padx=10, pady=5)

    # ---- 服务配置区 ----
    service_frame = customtkinter.CTkFrame(controller)
    service_frame.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
    service_frame.grid_columnconfigure(0, weight=1)
    service_frame.grid_columnconfigure(1, weight=1)

    # UDP 配置
    udp_frame = customtkinter.CTkFrame(service_frame)
    udp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    udp_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(udp_frame, text="本地日志 (UDP)").grid(row=0, column=0, columnspan=3, padx=10, pady=5)
    customtkinter.CTkLabel(udp_frame, text="IP地址:").grid(row=1, column=0, padx=(10,0), pady=5, sticky="w")
    customtkinter.CTkEntry(udp_frame, textvariable=controller.udp_ip).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    customtkinter.CTkLabel(udp_frame, text="端口:").grid(row=2, column=0, padx=(10,0), pady=5, sticky="w")
    customtkinter.CTkEntry(udp_frame, textvariable=controller.udp_port).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # HTTP 配置
    http_frame = customtkinter.CTkFrame(service_frame)
    http_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    http_frame.grid_columnconfigure(1, weight=1)
    customtkinter.CTkLabel(http_frame, text="流量日志 (HTTP)").grid(row=0, column=0, columnspan=2, padx=10, pady=5)
    customtkinter.CTkLabel(http_frame, text="URL:").grid(row=1, column=0, padx=(10,0), pady=5, sticky="w")
    customtkinter.CTkEntry(http_frame, textvariable=controller.http_url, width=300).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # ---- 日志显示区 ----
    controller.log_textbox = customtkinter.CTkTextbox(controller, state="disabled")
    controller.log_textbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    # ---- 主控制区 ----
    control_frame = customtkinter.CTkFrame(controller)
    control_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
    control_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_columnconfigure(1, weight=1)

    controller.test_button = customtkinter.CTkButton(control_frame, text="测试发送", command=controller.test_send_all)
    controller.test_button.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

    controller.start_button = customtkinter.CTkButton(control_frame, text="开始处理", command=controller.start_processing)
    controller.start_button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
    controller.stop_button = customtkinter.CTkButton(control_frame, text="停止处理", command=controller.stop_processing, state="disabled")
    controller.stop_button.grid(row=1, column=1, padx=10, pady=(5, 10), sticky="ew")
