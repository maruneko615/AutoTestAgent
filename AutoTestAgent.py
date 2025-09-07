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
from datetime import datetime

class AutoTestAgent:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8587
        self.socket = None
        self.running = False
        self.connected = False

        # 按鍵映射 - 使用實際的 EInputKeyType 枚舉
        self.key_mapping = {
            "UP": EInputKeyType.INPUT_KEY_UP,
            "DOWN": EInputKeyType.INPUT_KEY_DOWN,
            "LEFT": EInputKeyType.INPUT_KEY_LEFT,
            "RIGHT": EInputKeyType.INPUT_KEY_RIGHT,
            "START": EInputKeyType.INPUT_KEY_START,
            "NITRO": EInputKeyType.INPUT_KEY_NITRO,
            "TEST": EInputKeyType.INPUT_KEY_TEST,
            "SERVICE": EInputKeyType.INPUT_KEY_SERVICE,
        }

        self.available_keys = ["UP", "DOWN", "LEFT", "RIGHT", "START"]

        # 智能選項選擇相關
        self.target_selections = {}
        self.last_input_time = {}
        self.last_index = {}
        self.target_reached = {}

        signal.signal(signal.SIGINT, self.signal_handler)
        self.initialize_targets()

    def signal_handler(self, signum, frame):
        self.log("程式已停止")
        self.running = False
        sys.exit(0)

    def initialize_targets(self):
        flow_options = {}

        for flow, options in flow_options.items():
            if options:
                target = random.choice(options)
                self.target_selections[flow] = target
                self.log(f"🎯 {flow} 流程目標: {target}")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        sys.stdout.flush()

        try:
            with open("AutoTestAgent.log", "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
                f.flush()
        except Exception as e:
            print(f"日誌寫入失敗: {e}")

    def create_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            return True
        except Exception as e:
            self.log(f"Socket 創建失敗: {e}")
            return False

    def register_role(self):
        try:
            role_message = "role:agent"
            self.socket.sendto(role_message.encode(), (self.host, self.port))

            response, addr = self.socket.recvfrom(1024)
            response_str = response.decode()

            if response_str == "ok:agent":
                return True
            else:
                self.log(f"角色註冊失敗，收到回應: {response_str}")
                return False
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

    def handle_option_selection(self, game_data, flow_state, current_index, target_option):
        current_time = time.time()
        flow_key = str(flow_state)

        if current_index == target_option:
            if flow_key not in self.target_reached:
                self.target_reached[flow_key] = current_time
                self.log(f"🎯 已選中目標選項: {target_option}")
                return None
                return None
        else:
            if flow_key in self.target_reached:
                del self.target_reached[flow_key]

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
        return None

    def get_alternative_input(self, flow_state):
        return "LEFT"

    def process_game_data(self, data):
        try:
            game_data = GameFlowData()
            game_data.ParseFromString(data)

            self.log(f"📥 接收遊戲數據:")
            self.log(f"   所有欄位: {game_data}")
            self.log(f"   狀態: {game_data.current_flow_state}")

            selected_key = random.choice(self.available_keys)

            input_command = InputCommand()
            input_command.key_type = self.key_mapping[selected_key]

            command_data = input_command.SerializeToString()
            self.socket.sendto(command_data, (self.host, self.port))

            self.log(f"📤 發送按鍵: {selected_key}")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"處理遊戲數據失敗: {e}")

    def listen_loop(self):
        while self.running and self.connected:
            try:
                data, addr = self.socket.recvfrom(4096)
                self.process_game_data(data)
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


