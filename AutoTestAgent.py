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
        self.sock = None
        self.running = False
        self.log_file = "AutoTestAgent.log"

        # 動態生成按鍵映射
        self.key_mapping = {}
        for enum_value in EInputKeyType.DESCRIPTOR.values:
            if enum_value.name.startswith("INPUT_KEY_") and enum_value.name != "INPUT_KEY_MAX":
                key_name = enum_value.name.replace("INPUT_KEY_", "")
                self.key_mapping[key_name] = enum_value.number

        # 可用按鍵列表（排除屏蔽按鍵）
        self.available_keys = [key for key in self.key_mapping.keys() if key not in ["EMERGENCY", "TEST", "LEFT_LEG", "RIGHT_LEG", "SERVICE"]]

        self.log(f"🎮 AutoTestAgent 啟動")
        self.log(f"📋 可用按鍵: {self.available_keys}")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
                f.flush()
        except Exception as e:
            print(f"日誌寫入失敗: {e}")

    def connect_to_game(self):
        while self.running:
            try:
                self.log("🔄 等待遊戲連線...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.settimeout(5.0)

                # 角色註冊
                self.sock.sendto(b"role:agent", (self.host, self.port))
                response, addr = self.sock.recvfrom(1024)

                if response.decode() == "ok:agent":
                    self.log("✅ 遊戲連線成功，開始接收數據")
                    return True
                else:
                    self.log(f"❌ 角色註冊失敗: {response.decode()}")

            except Exception as e:
                self.log(f"❌ 連線失敗: {e}")

            if self.sock:
                self.sock.close()
                self.sock = None

            if self.running:
                self.log("❌ 遊戲連線中斷，5秒後重試...")
                time.sleep(5)

        return False

    def listen_for_data(self):
        while self.running:
            try:
                if not self.sock:
                    if not self.connect_to_game():
                        continue

                data, addr = self.sock.recvfrom(4096)
                game_data = GameFlowData()
                game_data.ParseFromString(data)

                # 記錄接收到的遊戲數據
                self.log(f"📥 接收遊戲數據:")
                for field in game_data.DESCRIPTOR.fields:
                    field_value = getattr(game_data, field.name)
                    self.log(f"   {field.name}: {field_value}")

                # 處理遊戲狀態並發送輸入
                self.process_game_state(game_data)

            except socket.timeout:
                continue
            except Exception as e:
                self.log(f"❌ 數據接收錯誤: {e}")
                if self.sock:
                    self.sock.close()
                    self.sock = None

    def process_game_state(self, game_data):
        try:
            # 隨機選擇按鍵
            selected_key = random.choice(self.available_keys)

            # 創建輸入指令
            input_command = InputCommand()
            input_command.key_inputs.append(self.key_mapping[selected_key])
            input_command.is_key_down = True
            input_command.timestamp = int(time.time() * 1000)

            # 發送輸入指令
            command_data = input_command.SerializeToString()
            self.sock.sendto(command_data, (self.host, self.port))

            self.log(f"📤 發送輸入指令: {selected_key}")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"❌ 處理遊戲狀態錯誤: {e}")

    def start(self):
        self.running = True

        # 啟動監聽執行緒
        listen_thread = threading.Thread(target=self.listen_for_data)
        listen_thread.daemon = True
        listen_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.log("🛑 正在停止程式...")
        self.running = False
        if self.sock:
            self.sock.close()
        self.log("程式已停止")

def signal_handler(signum, frame):
    print("\n收到中斷信號，正在優雅退出...")
    agent.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    try:
        agent = AutoTestAgent()
        agent.start()
    except KeyboardInterrupt:
        agent.stop()
    finally:
        input("按 Enter 鍵結束...")

