#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 定制化指令: 每次都選拉斯維加斯

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
        self.log_file = "AutoTestAgent_Custom.log"

        # 按鍵映射 - 使用實際的 EInputKeyType 枚舉
        self.key_mapping = {
            "Up": EInputKeyType.INPUT_KEY_Up,
            "Throttle": EInputKeyType.INPUT_KEY_Throttle,
        }

        # 設置信號處理
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n收到中斷信號，正在關閉...")
        self.running = False

    def log_message(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
                f.flush()
        except Exception as e:
            print(f"寫入日誌失敗: {e}")

    def connect_to_game(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)

            # 角色註冊
            self.socket.sendto(b"role:agent", (self.host, self.port))
            response, addr = self.socket.recvfrom(1024)

            if response.decode() == "ok:agent":
                self.log_message("✅ 成功連接到遊戲並註冊為 agent")
                return True
            else:
                self.log_message(f"❌ 註冊失敗，收到回應: {response.decode()}")
                return False

        except Exception as e:
            self.log_message(f"❌ 連接失敗: {e}")
            return False

    def generate_input_command(self, game_data):
        # 定制化邏輯: 每次都選拉斯維加斯
        if hasattr(game_data, 'current_flow_state') and str(game_data.current_flow_state) == "Copyright":
            # 在 Copyright 狀態選擇拉斯維加斯 (使用 Up 按鍵)
            selected_key = "Up"
            self.log_message(f"🎯 定制化邏輯: 在 Copyright 狀態選擇拉斯維加斯，使用按鍵: {selected_key}")
        else:
            # 其他狀態使用隨機按鍵
            selected_key = random.choice(list(self.key_mapping.keys()))
            self.log_message(f"🎲 隨機選擇按鍵: {selected_key}")

        # 創建 InputCommand
        command = InputCommand()
        command.input_key = self.key_mapping[selected_key]

        return command

    def process_game_data(self, data):
        try:
            game_data = GameFlowData()
            game_data.ParseFromString(data)

            # 記錄接收到的遊戲數據
            self.log_message("📥 接收到遊戲數據:")
            for field, value in game_data.ListFields():
                self.log_message(f"  {field.name}: {value}")

            # 生成輸入指令
            input_command = self.generate_input_command(game_data)

            # 發送指令
            command_data = input_command.SerializeToString()
            self.socket.sendto(command_data, (self.host, self.port))

            # 記錄發送的指令
            self.log_message("📤 發送輸入指令:")
            for field, value in input_command.ListFields():
                self.log_message(f"  {field.name}: {value}")

            self.log_message("=" * 50)

        except Exception as e:
            self.log_message(f"❌ 處理遊戲數據時發生錯誤: {e}")

    def listen_for_messages(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                if data:
                    self.process_game_data(data)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.log_message(f"❌ 接收訊息時發生錯誤: {e}")
                    break

    def run(self):
        self.log_message("🚀 AutoTestAgent 啟動 (定制化版本)")
        self.log_message(f"📝 定制化指令: 每次都選拉斯維加斯")

        while True:
            if not self.running:
                break

            if self.connect_to_game():
                self.running = True
                self.listen_for_messages()

            if not self.running:
                break

            self.log_message("⏳ 5秒後重新嘗試連接...")
            time.sleep(5)

        if self.socket:
            self.socket.close()
        self.log_message("👋 AutoTestAgent 已關閉")

if __name__ == "__main__":
    try:
        agent = AutoTestAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n程式被用戶中斷")
    except Exception as e:
        print(f"程式執行錯誤: {e}")
    finally:
        input("按 Enter 鍵結束...")