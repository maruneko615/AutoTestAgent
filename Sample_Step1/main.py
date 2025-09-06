#!/usr/bin/env python3
"""
通用遊戲測試代理程式 - Sample 模板
🔧 AutoTestBuilder 會根據實際遊戲需求進行客製化修改

此程式是一個完全通用的 AutoTestAgent 模板，可以適應任何基於 Protocol Buffers 的遊戲。
主要特色：
- 動態 ProtoSchema 適應
- 模組化狀態處理
- 完整的測試流程支援
"""

import sys
import os
import time
import signal
import threading
import argparse
from datetime import datetime

# 雙輸出系統 - 同時輸出到控制台和檔案
class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()

# 設定雙輸出
dual_output = DualOutput('output.log')
sys.stdout = dual_output
print("📝 Log 輸出已啟用，檔案: output.log")

# 動態尋找 ProtoSchema 路徑
proto_loaded = False
proto_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'ProtoSchema'),
    os.path.join(os.path.dirname(__file__), 'ProtoSchema'),
    '/mnt/d/AutoTest/ProtoSchema'
]

for proto_path in proto_paths:
    if os.path.exists(proto_path):
        sys.path.append(proto_path)
        print(f"✓ 找到 ProtoSchema 路徑: {os.path.abspath(proto_path)}")
        proto_loaded = True
        break

if not proto_loaded:
    print("❌ 找不到 ProtoSchema 路徑")
    sys.exit(1)

# 動態導入 Proto 模組
try:
    import InputCommand_pb2 as InputCommand
    import GameFlowData_pb2 as GameFlowData
    print("✓ Proto modules loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import proto modules: {e}")
    sys.exit(1)

# 導入其他模組
from core.udp_manager import UDPManager as UDPSocketManager
from core.message_handler import MessageHandler
from core.statistics_manager import StatisticsManager
from flow.state_manager import StateManager
from config.target_parser import TargetParser

class CustomGameTestAgent:
    """通用遊戲測試代理程式 - Sample 模板
    🔧 AutoTestBuilder 會根據實際遊戲需求進行客製化修改
    """
    
    def __init__(self, requirement: str = "通用自動測試"):
        self.requirement = requirement
        self.running = False
        
        # 初始化核心元件
        self._init_components()
        
        # 設定信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🤖 通用遊戲測試代理程式已初始化 (Dynamic ProtoSchema Version)")
        print(f"🎯 測試需求: {self.requirement}")
        print("📡 目標伺服器: UDP Server")
    
    def _init_components(self):
        """初始化核心元件"""
        # UDP 管理器
        self.udp_manager = UDPSocketManager(
            server_url="udp://127.0.0.1:8587"
        )
        
        # 訊息處理器
        self.message_handler = MessageHandler()
        
        # 統計管理器
        self.statistics_manager = StatisticsManager()
        
        # 狀態管理器
        self.state_manager = StateManager()
        
        # 目標解析器
        self.target_parser = TargetParser()
        
        print("✓ 所有核心元件初始化完成")
    
    def start(self):
        """啟動測試代理程式"""
        print("🚀 啟動遊戲測試代理程式...")
        
        # 解析測試需求
        targets = self.target_parser.parse_requirement(self.requirement)
        if targets:
            print(f"🎯 解析需求成功: {self.target_parser.get_target_summary()}")
            self.state_manager.set_targets(targets)
        
        # 建立 UDP 連線
        self.udp_manager.connect(
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
    
    def stop(self):
        """停止測試代理程式"""
        print("🛑 停止遊戲測試代理程式...")
        self.running = False
        if hasattr(self, 'udp_manager'):
            self.udp_manager.close()
    
    def _on_open(self, ws):
        """UDP 連線建立回調"""
        print("✅ UDP 連線已建立")
        self.running = True
        self.statistics_manager.start_session()
        
        # 啟動統計報告線程
        def print_stats():
            while self.running:
                time.sleep(10)  # 每10秒輸出一次統計
                if self.running:
                    self.statistics_manager.print_statistics()
        
        stats_thread = threading.Thread(target=print_stats, daemon=True)
        stats_thread.start()
    
    def _on_message(self, ws, message):
        """處理接收到的訊息"""
        try:
            # 解析遊戲數據
            game_data = self.message_handler.parse_message(message)
            if game_data:
                # 更新狀態管理器狀態
                self.state_manager.update_game_state(game_data)
                
                # 生成並發送輸入
                input_command = self.state_manager.generate_input()
                if input_command:
                    # 在實際發送時印出 log
                    self._log_input_command(input_command)
                    
                    # 添加發送前的確認信息
                    print(f"🚀 準備發送輸入指令到 UDP...")
                    
                    self.udp_manager.send_message(input_command)
                    self.statistics_manager.record_input_sent()
                    
                    print(f"✅ 輸入指令發送完成")
                else:
                    # 如果沒有生成輸入，也要記錄
                    print(f"⏸️  本次循環沒有生成輸入指令")
                    
            # 更新統計
            self.statistics_manager.record_message_received()
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def _on_error(self, ws, error):
        """處理連線錯誤"""
        print(f"❌ UDP 錯誤: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """處理連線關閉"""
        print(f"🔌 UDP 連線已關閉 (狀態碼: {close_status_code})")
        self.running = False
        self.statistics_manager.end_session()
        self.state_manager.stop()
    
    def _signal_handler(self, signum, frame):
        """處理系統信號"""
        print(f"\n🛑 接收到停止信號 ({signum})")
        self.stop()
        dual_output.close()
        sys.exit(0)

    def _log_input_command(self, input_command: bytes):
        """解析並印出輸入指令的 log"""
        try:
            # TODO: 🔧 需要解析 InputCommand_pb2 結構 - 來源: AutoTest_Game_Setting.md
            # 嘗試解析輸入指令
            input_cmd = InputCommand.InputCommand()
            input_cmd.ParseFromString(input_command)
            
            # 獲取按鍵名稱
            key_names = []
            for key in input_cmd.key_inputs:
                key_name = self._get_key_name(key)
                key_names.append(key_name)
            
            if key_names:
                action = "按下" if input_cmd.is_key_down else "釋放"
                print(f"📤 發送{action}輸入指令: [{', '.join(key_names)}]")
            
        except Exception as e:
            print(f"📤 發送輸入指令 ({len(input_command)} bytes)")
    
    def _get_key_name(self, key_value: int) -> str:
        """獲取按鍵名稱"""
        # TODO: 🔧 需要從 AutoTest_Game_Setting.md 的 EInputKeyType 枚舉取得按鍵名稱
        key_names = {
            0: "UP",    # TODO: 🔧 對應 EInputKeyType::Up
            1: "DOWN",  # TODO: 🔧 對應 EInputKeyType::Down  
            2: "LEFT",  # TODO: 🔧 對應 EInputKeyType::Left
            3: "RIGHT", # TODO: 🔧 對應 EInputKeyType::Right
            4: "START", # TODO: 🔧 對應 EInputKeyType::Start
            5: "NITRO", # TODO: 🔧 對應 EInputKeyType::Nitro
            8: "COIN",  # TODO: 🔧 對應 EInputKeyType::Coin
        }
        return key_names.get(key_value, f"UNKNOWN_KEY_{key_value}")

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description='通用遊戲測試代理程式 - Sample 模板')
    parser.add_argument('--requirement', '-r',
                       default="通用自動測試",
                       help='測試需求描述')
    parser.add_argument('--url', '-u',
                       default="udp://127.0.0.1:8587",
                       help='Server URL (UDP Socket connection)')
    
    args = parser.parse_args()
    
    try:
        # 創建並啟動測試代理程式
        agent = CustomGameTestAgent(requirement=args.requirement)
        agent.start()
        
        # 保持程式運行
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 使用者中斷程式")
    except Exception as e:
        print(f"❌ 程式執行錯誤: {e}")
    finally:
        if 'agent' in locals():
            agent.stop()
        dual_output.close()

if __name__ == "__main__":
    main()
