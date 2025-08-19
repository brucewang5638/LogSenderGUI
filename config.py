# config.py
# 负责加载和提供应用配置
import yaml
import os
import json

# --- 全局配置变量 ---
# 在应用启动时，会从 config.yml 文件加载配置到这个字典中
APP_CONFIG = {}

def load_config():
    """
    从 config.yml 文件加载配置。
    如果文件不存在或加载失败，将使用默认值。
    """
    global APP_CONFIG
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            APP_CONFIG = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load config.yml: {e}. Using default values.")
        # 如果配置文件加载失败，提供一个默认结构以避免程序崩溃
        APP_CONFIG = {
            'log_sender': {
                'http_url': 'http://127.0.0.1:19762/V1/log',
                'udp_ip': '127.0.0.1',
                'udp_port': 19708
            },
            'event_validator': {
                'event_list_url': 'http://127.0.0.1:8080/api/events'
            }
        }

# --- 在模块加载时执行配置加载 ---
load_config()

# --- 提供便捷的配置访问接口 ---
def get_log_sender_config():
    return APP_CONFIG.get('log_sender', {})

def get_event_validator_config():
    return APP_CONFIG.get('event_validator', {})

def get_complete_event_list():
    return APP_CONFIG.get('complete_event_list', [])


# --- 为了兼容旧代码，可以保留这些常量，但值从新配置中获取 ---
log_sender_cfg = get_log_sender_config()
DEFAULT_UDP_IP = log_sender_cfg.get('udp_ip', '127.0.0.1')
DEFAULT_UDP_PORT = str(log_sender_cfg.get('udp_port', 19708))
DEFAULT_HTTP_URL = log_sender_cfg.get('http_url', 'http://127.0.0.1:19762/V1/log')

event_validator_cfg = get_event_validator_config()
DEFAULT_EVENT_LIST_URL = event_validator_cfg.get('event_list_url', 'http://127.0.0.1:8080/api/events')
DEFAULT_EVENT_TOKEN = event_validator_cfg.get('default_token', '')
# 将payload字典转换为格式化的JSON字符串，如果不存在则为空字符串
default_payload_dict = event_validator_cfg.get('default_payload', None)
DEFAULT_EVENT_PAYLOAD = json.dumps(default_payload_dict, indent=4, ensure_ascii=False) if default_payload_dict else ""
