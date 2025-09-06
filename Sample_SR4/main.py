#!/usr/bin/env python3
"""
SR4 AutoTest Agent - 模組化版本
支援目標導向和隨機測試模式
"""

import sys
import os
import time
import uuid
import threading
import argparse
import logging
from datetime import datetime

# 修復 protobuf 版本相容性問題（必須在任何 pb2 檔案匯入前設定）
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import InputCommand_pb2 as InputCommand
    import GameFlowData_pb2 as GameFlowData
    print("✓ Proto modules loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import proto modules: {e}")
    print(f"Proto path: {proto_path}")
    sys.exit(1)

from core.udp_manager import UDPManager as UDPSocketManager
from core.message_handler import MessageHandler
from core.statistics_manager import StatisticsManager
from flow.state_manager import StateManager
from config.target_parser import TargetParser

class DualLogger:
    """雙重輸出 Logger - 同時輸出到螢幕和檔案"""
    
    def __init__(self, log_file="output.log"):
        self.log_file = log_file
        self.file_handle = None
        self._setup_logging()
        
    def _setup_logging(self):
        """設定日誌系統"""
        try:
            # 開啟檔案用於寫入
            self.file_handle = open(self.log_file, 'w', encoding='utf-8')
            
            # 重定向 print 函數
            self.original_print = print
            import builtins
            builtins.print = self._dual_print
            
            print(f"📝 Log 輸出已啟用，檔案: {self.log_file}")
            
        except Exception as e:
            print(f"❌ 無法設定 log 檔案: {e}")
            
    def _dual_print(self, *args, **kwargs):
        """自定義 print 函數 - 同時輸出到螢幕和檔案"""
        # 輸出到螢幕
        self.original_print(*args, **kwargs)
        
        # 輸出到檔案
        if self.file_handle:
            try:
                # 處理參數，轉換為字串
                message = ' '.join(str(arg) for arg in args)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.file_handle.write(f"[{timestamp}] {message}\n")
                self.file_handle.flush()  # 立即寫入檔案
            except Exception as e:
                self.original_print(f"❌ 寫入 log 檔案失敗: {e}")
                
    def close(self):
        """關閉 log 檔案"""
        if self.file_handle:
            try:
                self.file_handle.close()
                print(f"📝 Log 檔案已關閉: {self.log_file}")
            except:
                pass
            
        # 恢復原始 print 函數
        import builtins
        builtins.print = self.original_print

class SR4TestAgent:
    def __init__(self, server_url="udp://127.0.0.1:8587", requirement=None, enable_log=True):
        self.server_url = server_url
        self.requirement = requirement
        self.session_id = str(uuid.uuid4())
        self.running = False
        
        # 初始化雙重 Logger
        self.logger = None
        if enable_log:
            self.logger = DualLogger("output.log")
        
        print(f"🤖 SR4 Test Agent initialized (Modular Version)")
        print(f"📡 Target server: {server_url}")
        print(f"🎮 Session ID: {self.session_id}")
        print(f"📋 Requirement: {requirement or 'Random Mode'}")
        
        # 初始化各模組
        self.udp_manager = UDPSocketManager(server_url)
        self.message_handler = MessageHandler()
        self.statistics_manager = StatisticsManager()
        self.state_manager = StateManager()
        
        # 解析目標需求
        self.target_parser = TargetParser()
        self.targets = self.target_parser.parse_requirement(requirement)
        
        print(f"🎯 Parsed targets: {self.targets}")
        
        # 設定流程管理器的目標
        self.state_manager.set_targets(self.targets)
        
    def start(self):
        """啟動測試代理"""
        print("🚀 Starting SR4 Test Agent...")
        print("=" * 50)
        
        try:
            self.udp_manager.connect(
                on_message=self._on_message,
                on_open=self._on_open,
                on_close=self._on_close,
                on_error=self._on_error
            )
        except KeyboardInterrupt:
            print("\n👋 Agent stopped by user")
        except Exception as e:
            print(f"❌ Agent error: {e}")
        finally:
            self.stop()
        
    def _on_message(self, message):
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
            
    def _on_open(self):
        """連線建立回調"""
        print("🔗 UDP connection established")
        self.running = True
        self.statistics_manager.start_session()
        self.state_manager.start()
        
        # 啟動統計報告線程
        self.stats_thread = threading.Thread(target=self._stats_loop, daemon=True)
        self.stats_thread.start()
        
    def _on_close(self):
        """連線關閉回調"""
        print("🔌 UDP connection closed")
        self.running = False
        self.statistics_manager.end_session()
        self.state_manager.stop()
        
    def _on_error(self, error):
        """UDP錯誤回調"""
        print(f"❌ UDP error: {error}")
        
    def _stats_loop(self):
        """統計資訊報告循環"""
        while self.running:
            time.sleep(5)  # 每5秒報告一次
            if self.running:
                self.statistics_manager.print_stats()
                
    def stop(self):
        """停止Agent"""
        print("⏹️  Stopping agent...")
        self.running = False
        self.udp_manager.close()
        
        # 關閉 Logger
        if self.logger:
            self.logger.close()
    
    def _log_input_command(self, input_command: bytes):
        """解析並印出輸入指令的 log"""
        try:
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
        key_names = {
            0: "UP",
            1: "DOWN", 
            2: "LEFT",
            3: "RIGHT",
            4: "START",
            5: "TEST",
            6: "SERVICE",
            7: "COIN"
        }
        return key_names.get(key_value, f"KEY_{key_value}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='SR4 AutoTest Agent - Modular Version')
    parser.add_argument('--server', default='udp://127.0.0.1:8587', help='Server URL (UDP Socket connection)')
    parser.add_argument('--requirement', help='Test requirement string (e.g., "選擇首爾正走，開極速王者")')
    parser.add_argument('--no-log', action='store_true', help='Disable log file output')
    parser.add_argument('--log-file', default='output.log', help='Log file name (default: output.log)')
    
    args = parser.parse_args()
    
    # 決定是否啟用 log
    enable_log = not args.no_log
    
    agent = SR4TestAgent(args.server, args.requirement, enable_log)
    
    # 如果有指定 log 檔案名稱，更新 logger
    if enable_log and args.log_file != 'output.log':
        agent.logger.log_file = args.log_file
        agent.logger.file_handle.close()
        agent.logger.file_handle = open(args.log_file, 'w', encoding='utf-8')
        print(f"📝 Log 檔案已更新為: {args.log_file}")
    
    agent.start()

if __name__ == "__main__":
    main()
