#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 確保正確的工作目錄和路徑
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

try:
    from ProtoSchema.GameFlowData_pb2 import GameFlowData
    from ProtoSchema.InputCommand_pb2 import InputCommand, EInputKeyType
    print("✅ Protobuf 模組載入成功")
except ImportError as e:
    print(f"❌ 無法導入 Protobuf 模組: {e}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

import socket
import threading
import time
import random
import signal

class AutoTestAgent:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8587
        self.socket = None
        self.running = False
        self.connected = False
        self.log_file = None

        # 智能選項選擇相關
        self.target_selections = {}
        self.last_input_time = {}
        self.last_index = {}
        self.target_reached = {}

        # 動態生成按鍵映射
        self.key_mapping = {}
        for enum_value in EInputKeyType.DESCRIPTOR.values:
            if enum_value.name.startswith("INPUT_KEY_") and enum_value.name != "INPUT_KEY_MAX":
                key_name = enum_value.name.replace("INPUT_KEY_", "")
                self.key_mapping[key_name] = enum_value.number

        # 可用按鍵（排除屏蔽按鍵）
        self.available_keys = [key for key in self.key_mapping.keys() if key not in ["EMERGENCY", "TEST", "LEFT_LEG", "RIGHT_LEG", "SERVICE"]]

        signal.signal(signal.SIGINT, self.signal_handler)
        self.initialize_log()
        self.initialize_targets()

    def signal_handler(self, signum, frame):
        self.log("程式已停止")
        self.running = False
        if self.log_file:
            self.log_file.close()
        sys.exit(0)

    def initialize_log(self):
        try:
            self.log_file = open("AutoTestAgent.log", "w", encoding="utf-8")
        except Exception as e:
            print(f"無法創建日誌文件: {e}")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if self.log_file:
            self.log_file.write(log_message + "\n")
            self.log_file.flush()

    def initialize_targets(self):
        flow_options = {}

        for flow, options in flow_options.items():
            if options:
                target = random.choice(options)
                self.target_selections[flow] = target
                self.log(f"🎯 {flow} 流程目標: {target}")

    def create_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            return True
        except Exception as e:
            self.log(f"創建 Socket 失敗: {e}")
            return False

    def register_role(self):
        try:
            self.socket.sendto(b"role:agent", (self.host, self.port))
            response, addr = self.socket.recvfrom(1024)
            if response.decode() == "ok:agent":
                return True
        except Exception as e:
            self.log(f"角色註冊失敗: {e}")
        return False

    def connect_to_game(self):
        while self.running:
            self.log("🔄 等待遊戲連線...")
            if self.create_socket() and self.register_role():
                self.connected = True
                self.log("✅ 遊戲連線成功，開始接收數據")
                return True
            else:
                self.log("❌ 遊戲連線失敗，5秒後重試...")
                time.sleep(5)
        return False

    def process_game_data(self, data):
        try:
            game_data = GameFlowData()
            game_data.ParseFromString(data)

            self.log("📥 接收遊戲數據:")
            for field in game_data.DESCRIPTOR.fields:
                field_value = getattr(game_data, field.name)
                self.log(f"   {field.name}: {field_value}")

            selected_key = self.generate_input(game_data)
            if selected_key:
                self.send_input_command(selected_key)

            self.log("=" * 50)

        except Exception as e:
            self.log(f"處理遊戲數據失敗: {e}")

    def generate_input(self, game_data):
        if hasattr(game_data, 'current_flow_state'):
            flow_state = game_data.current_flow_state

            # 檢查是否為有操作邏輯的流程
            if flow_state in self.target_selections:
                current_index = getattr(game_data, 'current_option_index', 0)
                target_option = self.target_selections[flow_state]
                return self.handle_option_selection(game_data, flow_state, current_index, target_option)

        # 預設隨機輸入
        return random.choice(self.available_keys)

    def handle_option_selection(self, game_data, flow_state, current_index, target_option):
        current_time = time.time()
        flow_key = str(flow_state)

        # 檢查是否已達到目標
        if current_index == target_option:
            if flow_key not in self.target_reached:
                self.target_reached[flow_key] = current_time
                self.log(f"🎯 已選中目標選項: {target_option}")
                return None
                return None
        else:
            if flow_key in self.target_reached:
                del self.target_reached[flow_key]

        # 檢查輸入頻率
        if flow_key in self.last_input_time:
            if current_time - self.last_input_time[flow_key] < 1.0:
                if flow_key in self.last_index and self.last_index[flow_key] == current_index:
                    self.last_input_time[flow_key] = current_time
                    self.last_index[flow_key] = current_index
                    return self.get_alternative_input(flow_state)
                else:
                    return None

        self.last_input_time[flow_key] = current_time
        self.last_index[flow_key] = current_index

        return self.get_navigation_input(flow_state, current_index, target_option)

    def get_navigation_input(self, flow_state, current_index, target_index):
        return "RIGHT"

    def get_alternative_input(self, flow_state):
        return "LEFT"

    def send_input_command(self, key_name):
        try:
            input_command = InputCommand()
            input_command.key_inputs.append(self.key_mapping[key_name])
            input_command.is_key_down = True
            input_command.timestamp = int(time.time() * 1000)

            data = input_command.SerializeToString()
            self.socket.sendto(data, (self.host, self.port))

            self.log(f"📤 發送輸入指令: {key_name}")

        except Exception as e:
            self.log(f"發送輸入指令失敗: {e}")

    def listen_loop(self):
        while self.running and self.connected:
            try:
                data, addr = self.socket.recvfrom(4096)
                self.process_game_data(data)
            except socket.timeout:
                continue
            except Exception as e:
                self.log(f"❌ 遊戲連線中斷: {e}")
                self.connected = False
                break

    def run(self):
        self.running = True
        while self.running:
            if self.connect_to_game():
                self.listen_loop()
            if self.running:
                self.log("❌ 遊戲連線中斷，5秒後重試...")
                time.sleep(5)

def main():
    try:
        agent = AutoTestAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n程式已停止")
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()

