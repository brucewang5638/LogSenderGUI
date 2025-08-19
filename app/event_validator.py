# app/event_validator.py
import requests
import json

class EventValidator:
    """
    负责处理事件校验的核心业务逻辑。
    """
    def __init__(self, logger_callback, complete_event_list):
        """
        初始化校验器。
        :param logger_callback: 用于记录日志的回调函数。
        :param complete_event_list: 从配置加载的完整事件名称列表。
        """
        self.logger = logger_callback
        self.set_complete_event_list(complete_event_list) # Use the new setter here too

    def set_complete_event_list(self, new_list):
        """
        更新完整的事件名称列表。
        """
        self.complete_event_names = set(new_list)
        self.logger(f"事件校验器：完整事件列表已更新，共 {len(new_list)} 个事件。")

    def validate_events(self, method, url, token, payload_str):
        """
        根据指定的参数发起请求，获取事件列表，并找出缺失的事件。
        :param method: 请求方法 (e.g., "GET", "POST").
        :param url: 事件列表的API URL.
        :param token: 用于认证的Cookie/Token字符串。
        :param payload_str: JSON格式的请求载荷字符串。
        :return: 一个元组 (success, message_or_data)。
        """
        self.logger(f"开始事件校验: {method} {url}")

        headers = {}
        if token:
            headers['Cookie'] = token
            self.logger("已添加Cookie到请求头。" )

        payload = None
        if method == 'POST' and payload_str:
            try:
                payload = json.loads(payload_str)
                self.logger("请求载荷解析成功。" )
            except json.JSONDecodeError:
                error_msg = "请求载荷错误: 输入的内容不是有效的JSON格式。"
                self.logger(error_msg)
                return False, error_msg

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()  # 检查HTTP错误
        except requests.exceptions.RequestException as e:
            error_msg = f"网络错误: 请求失败 -> {e}"
            self.logger(error_msg)
            return False, error_msg

        try:
            json_data = response.json()
        except json.JSONDecodeError:
            error_msg = "解析错误: 响应内容不是有效的JSON格式。"
            self.logger(error_msg)
            return False, error_msg

        # --- 核心校验逻辑 ---
        if (
            not isinstance(json_data, dict) or
            "data" not in json_data or
            not isinstance(json_data.get("data"), dict) or
            "list" not in json_data["data"] or
            not isinstance(json_data["data"].get("list"), list)
        ):
            # 将接收到的数据（部分）加入错误日志，方便调试
            received_data_preview = str(json_data)[:200]
            error_msg = (
                f"数据格式错误: JSON结构不符合预期 (应为 {{'data': {{'list': [...]}}}})。\n"
                f"收到的内容 (前200字符): {received_data_preview}"
            )
            self.logger(error_msg)
            return False, error_msg

        # 提取并去重 eventName
        extracted_names = {item["eventName"] for item in json_data["data"]["list"] if "eventName" in item}
        self.logger(f"成功获取并去重后，得到 {len(extracted_names)} 个事件。" )

        # 找出缺少的事件
        missing_names = self.complete_event_names - extracted_names
        self.logger(f"比对完成，发现 {len(missing_names)} 个缺失的事件。" )

        return True, {
            "extracted_count": len(extracted_names),
            "missing_count": len(missing_names),
            "missing_names": sorted(list(missing_names))
        }
