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
        self.log_file = "AutoTestAgentLog.txt"

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

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.log("程式已停止")
        self.running = False
        sys.exit(0)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
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
            self.log(f"建立 Socket 失敗: {e}")
            return False

    def register_role(self):
        try:
            self.socket.sendto(b"role:agent", (self.host, self.port))
            response, addr = self.socket.recvfrom(1024)
            if response == b"ok:agent":
                return True
            else:
                self.log(f"角色註冊失敗，收到回應: {response}")
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

    def process_game_data(self, data):
        try:
            game_data = GameFlowData()
            game_data.ParseFromString(data)

            self.log(f"📥 接收遊戲數據:")
            self.log(f"   所有欄位: {game_data}")
            self.log(f"   狀態: {game_data.current_flow_state}")
            self.log("=" * 50)

            self.send_random_input()

        except Exception as e:
            self.log(f"處理遊戲數據失敗: {e}")

    def send_random_input(self):
        try:
            random_key = random.choice(self.available_keys)

            input_command = InputCommand()
            input_command.input_key = self.key_mapping[random_key]

            serialized_data = input_command.SerializeToString()
            self.socket.sendto(serialized_data, (self.host, self.port))

            self.log(f"📤 發送輸入指令: {random_key}")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"發送輸入指令失敗: {e}")

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

def main():
    try:
        agent = AutoTestAgent()
        agent.run()
    except KeyboardInterrupt:
        print("程式已停止")
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()


