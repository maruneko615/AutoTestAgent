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
    from ProtoSchema.InputCommand_pb2 import InputCommand
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

        # 遊戲狀態定義
        self.game_states = ["Flow1", "Flow2", "Flow3", "Flow4", "Flow5", "Flow6"]

        # 按鍵映射
        self.key_mapping = {
            "Key1": 0,
            "Key2": 1,
            "Key3": 2,
            "Key4": 3,
            "Key5": 4,
            "Key6": 5,
            "Key7": 6
        }

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        self.log("程式已停止")
        self.running = False
        sys.exit(0)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        # 輸出到控制台
        print(log_message)

        # 輸出到檔案
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
            self.log(f"Socket 創建失敗: {e}")
            return False

    def register_role(self):
        try:
            # 發送角色註冊
            self.socket.sendto("role:agent".encode('utf-8'), (self.host, self.port))

            # 等待確認
            data, addr = self.socket.recvfrom(1024)
            message = data.decode('utf-8')

            if message == "ok:agent":
                self.log("角色註冊成功")
                return True
            else:
                self.log(f"角色註冊失敗: {message}")
                return False
        except Exception as e:
            self.log(f"角色註冊異常: {e}")
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

    def create_input_command(self, keys):
        input_cmd = InputCommand()
        for key in keys:
            if key in self.key_mapping:
                input_cmd.key_inputs.append(self.key_mapping[key])
        input_cmd.is_key_down = True
        input_cmd.timestamp = int(time.time() * 1000)
        return input_cmd.SerializeToString()

    def process_game_data(self, data):
        try:
            # 解析遊戲數據
            game_data = GameFlowData()
            game_data.ParseFromString(data)

            self.log(f"📥 接收遊戲數據: 狀態={game_data.current_flow_state}")
            self.log("=" * 50)

            # 生成隨機輸入
            random_key = random.choice(list(self.key_mapping.keys()))
            input_command = self.create_input_command([random_key])

            # 發送輸入指令
            self.socket.sendto(input_command, (self.host, self.port))
            self.log(f"📤 發送輸入指令: {random_key}")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"處理遊戲數據失敗: {e}")

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
        self.log("AutoTestAgent 啟動")

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


