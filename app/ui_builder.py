# app/ui_builder.py
import customtkinter

def create_widgets(controller):
    """
    创建并布局所有UI组件。
    使用Tabview来组织UI，并将所有事件绑定到controller实例的方法上。
    """
    # ---- 主体网格布局 ----
    controller.grid_columnconfigure(0, weight=1)
    controller.grid_rowconfigure(0, weight=1) # Tabview将占据大部分空间

    # ---- 创建Tab视图 ----
    tab_view = customtkinter.CTkTabview(controller)
    tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    tab_log_sender = tab_view.add("日志发送")
    tab_event_validator = tab_view.add("事件校验")

    # ---- 日志显示区 (共享) ----
    # 将日志区放在Tab外部，使其在切换Tab时保持可见
    controller.log_textbox = customtkinter.CTkTextbox(controller, state="disabled", height=150)
    controller.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # ---- 构建“日志发送”选项卡 ----
    build_log_sender_tab(tab_log_sender, controller)

    # ---- 构建“事件校验”选项卡 ----
    build_event_validator_tab(tab_event_validator, controller)


def build_log_sender_tab(tab, controller):
    """构建日志发送功能相关的UI组件"""
    tab.grid_columnconfigure(0, weight=1)

    # -- 目录选择区 --
    dir_frame = customtkinter.CTkFrame(tab)
    dir_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    dir_frame.grid_columnconfigure(1, weight=1)

    customtkinter.CTkLabel(dir_frame, text="原始日志目录:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    customtkinter.CTkEntry(dir_frame, textvariable=controller.source_dir, state="readonly").grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    customtkinter.CTkButton(dir_frame, text="浏览...", command=controller.browse_source_dir).grid(row=0, column=2, padx=10, pady=5)

    customtkinter.CTkLabel(dir_frame, text="已处理目录:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    customtkinter.CTkEntry(dir_frame, textvariable=controller.processed_dir, state="readonly").grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    customtkinter.CTkButton(dir_frame, text="浏览...", command=controller.browse_processed_dir).grid(row=1, column=2, padx=10, pady=5)

    # -- 服务配置区 --
    service_frame = customtkinter.CTkFrame(tab)
    service_frame.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
    service_frame.grid_columnconfigure(0, weight=1)
    service_frame.grid_columnconfigure(1, weight=1)

    udp_frame = customtkinter.CTkFrame(service_frame)
    udp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    udp_frame.grid_columnconfigure(1, weight=1)
    customtkinter.CTkLabel(udp_frame, text="本地日志 (UDP)").pack(anchor="w", padx=10, pady=5)
    customtkinter.CTkLabel(udp_frame, text="IP地址:").pack(anchor="w", padx=10)
    customtkinter.CTkEntry(udp_frame, textvariable=controller.udp_ip).pack(fill="x", padx=10, pady=(0, 5))
    customtkinter.CTkLabel(udp_frame, text="端口:").pack(anchor="w", padx=10)
    customtkinter.CTkEntry(udp_frame, textvariable=controller.udp_port).pack(fill="x", padx=10, pady=(0, 10))

    http_frame = customtkinter.CTkFrame(service_frame)
    http_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    http_frame.grid_columnconfigure(1, weight=1)
    customtkinter.CTkLabel(http_frame, text="流量日志 (HTTP)").pack(anchor="w", padx=10, pady=5)
    customtkinter.CTkLabel(http_frame, text="URL:").pack(anchor="w", padx=10)
    customtkinter.CTkEntry(http_frame, textvariable=controller.http_url, width=300).pack(fill="x", padx=10, pady=(0, 10))

    # -- 主控制区 --
    control_frame = customtkinter.CTkFrame(tab)
    control_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    control_frame.grid_columnconfigure((0, 1), weight=1)

    controller.test_button = customtkinter.CTkButton(control_frame, text="测试发送", command=controller.test_send_all)
    controller.test_button.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

    controller.start_button = customtkinter.CTkButton(control_frame, text="开始处理", command=controller.start_processing)
    controller.start_button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
    controller.stop_button = customtkinter.CTkButton(control_frame, text="停止处理", command=controller.stop_processing, state="disabled")
    controller.stop_button.grid(row=1, column=1, padx=10, pady=(5, 10), sticky="ew")


def build_event_validator_tab(tab, controller):
    """构建事件校验功能相关的UI组件，采用两栏布局"""
    # --- 主体两栏布局 ---
    tab.grid_columnconfigure(0, weight=0) # 左侧配置栏，不扩展
    tab.grid_columnconfigure(1, weight=1) # 右侧结果栏，随窗口扩展
    tab.grid_rowconfigure(0, weight=1)

    # --- 左侧配置栏 ---
    left_frame = customtkinter.CTkFrame(tab)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
    left_frame.grid_columnconfigure(0, weight=1)

    # -- 请求配置区 --
    config_frame = customtkinter.CTkFrame(left_frame)
    config_frame.grid(row=0, column=0, padx=10, pady=0, sticky="ew")
    config_frame.grid_columnconfigure(1, weight=1)

    customtkinter.CTkLabel(config_frame, text="请求URL:").grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
    customtkinter.CTkEntry(config_frame, textvariable=controller.event_list_url).grid(row=0, column=1, columnspan=2, padx=10, pady=0, sticky="ew")

    customtkinter.CTkLabel(config_frame, text="请求方法:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    customtkinter.CTkOptionMenu(config_frame, variable=controller.event_req_method, values=["GET", "POST"]).grid(row=1, column=1, padx=10, pady=5, sticky="w")

    customtkinter.CTkLabel(config_frame, text="Token/Cookie:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    customtkinter.CTkEntry(config_frame, textvariable=controller.event_req_token, placeholder_text="可选").grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    # -- 请求载荷区 --
    left_frame.grid_rowconfigure(1, weight=1) # 让载荷区填充剩余空间
    payload_frame = customtkinter.CTkFrame(left_frame)
    payload_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    payload_frame.grid_columnconfigure(0, weight=1)
    payload_frame.grid_rowconfigure(1, weight=1)

    customtkinter.CTkLabel(payload_frame, text="请求载荷 (JSON)").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    controller.validator_payload_textbox = customtkinter.CTkTextbox(payload_frame)
    controller.validator_payload_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # -- 控制区 --
    controller.validate_button = customtkinter.CTkButton(left_frame, text="开始校验", command=controller.start_validation)
    controller.validate_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    # --- 右侧结果栏 ---
    right_frame = customtkinter.CTkFrame(tab)
    right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_rowconfigure(1, weight=1)

    customtkinter.CTkLabel(right_frame, text="校验结果").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    controller.validator_results_textbox = customtkinter.CTkTextbox(right_frame, state="disabled")
    controller.validator_results_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
