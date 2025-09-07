#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
import time
import random
import signal
import threading
from datetime import datetime

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

class AutoTestAgent:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8587
        self.socket = None
        self.running = False
        self.connected = False
        self.log_file = None

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

        # 初始化日誌
        self.init_log()

        # 設置信號處理
        signal.signal(signal.SIGINT, self.signal_handler)

    def init_log(self):
        try:
            self.log_file = open("AutoTestAgent.log", "w", encoding="utf-8")
            self.log("🚀 AutoTestAgent 啟動")
        except Exception as e:
            print(f"❌ 無法創建日誌文件: {e}")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        # 輸出到控制台
        print(log_message)

        # 輸出到文件
        if self.log_file:
            self.log_file.write(log_message + "\n")
            self.log_file.flush()

    def signal_handler(self, signum, frame):
        self.log("程式已停止")
        self.running = False
        if self.log_file:
            self.log_file.close()
        sys.exit(0)

    def create_socket(self):
        try:
            if self.socket:
                self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            return True
        except Exception as e:
            self.log(f"❌ 創建 Socket 失敗: {e}")
            return False

    def register_role(self):
        try:
            # 發送角色註冊
            self.socket.sendto(b"role:agent", (self.host, self.port))

            # 等待確認
            data, addr = self.socket.recvfrom(1024)
            if data.decode() == "ok:agent":
                self.log("✅ 角色註冊成功")
                return True
            else:
                self.log(f"❌ 角色註冊失敗，收到: {data.decode()}")
                return False
        except Exception as e:
            self.log(f"❌ 角色註冊異常: {e}")
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

            # 記錄接收的遊戲數據
            self.log(f"📥 接收遊戲數據:")
            self.log(f"   所有欄位: {game_data}")
            self.log(f"   狀態: {game_data.current_flow_state}")

            # 生成隨機輸入
            self.send_random_input()

            self.log("=" * 50)

        except Exception as e:
            self.log(f"❌ 處理遊戲數據失敗: {e}")

    def send_random_input(self):
        try:
            # 選擇隨機按鍵
            random_key = random.choice(self.available_keys)

            # 創建輸入指令
            input_command = InputCommand()
            input_command.key_inputs.append(self.key_mapping[random_key])
            input_command.is_key_down = True
            input_command.timestamp = int(time.time() * 1000)

            # 發送指令
            self.socket.sendto(input_command.SerializeToString(), (self.host, self.port))

            self.log(f"📤 發送輸入指令: {random_key}")

        except Exception as e:
            self.log(f"❌ 發送輸入指令失敗: {e}")

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
        print(f"❌ 程式執行錯誤: {e}")
        input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()

