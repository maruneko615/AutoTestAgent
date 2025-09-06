"""
UDP Socket 連線管理模組
負責建立、維護和關閉 UDP 連線
保持與 UDPSocket 管理器相同的 API 接口
"""

import socket
import threading
import time
from typing import Callable, Optional

class UDPManager:
    def __init__(self, server_url: str):
        # 解析 server_url (格式: ws://127.0.0.1:8587 或 udp://127.0.0.1:8587)
        if server_url.startswith('ws://'):
            server_url = server_url.replace('ws://', 'udp://')
        elif server_url.startswith('udp://'):
            pass
        else:
            server_url = f"udp://{server_url}"
            
        # 解析主機和端口
        url_parts = server_url.replace('udp://', '').split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1]) if len(url_parts) > 1 else 8587
        
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None
        
        # 角色註冊狀態
        self._role_registered = False
        self._waiting_for_role_confirmation = False
        
        # 回調函數
        self.on_message_callback: Optional[Callable] = None
        self.on_open_callback: Optional[Callable] = None
        self.on_close_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
    def connect(self, on_message: Callable, on_open: Callable, on_close: Callable, on_error: Callable):
        """建立 UDP 連線"""
        try:
            # 創建 UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)  # 設定超時
            
            # 保存回調函數
            self.on_message_callback = on_message
            self.on_open_callback = on_open
            self.on_close_callback = on_close
            self.on_error_callback = on_error
            
            # 標記為運行狀態
            self.running = True
            
            # 啟動接收線程
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # 執行角色註冊
            if self._perform_role_registration():
                # 註冊成功後調用 on_open 回調
                if self.on_open_callback:
                    self.on_open_callback()
                print(f"✅ UDP 連線建立成功: {self.host}:{self.port}")
            else:
                raise ConnectionError("角色註冊失敗")
            
            # 保持主線程運行 (模擬 UDPSocket 的 run_forever)
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n👋 收到中斷信號，正在關閉...")
                
        except Exception as e:
            print(f"❌ UDP 連線失敗: {e}")
            if self.on_error_callback:
                self.on_error_callback(e)
            raise
    
    def _perform_role_registration(self) -> bool:
        """執行角色註冊流程"""
        print("🔐 開始角色註冊...")
        
        try:
            # 發送角色識別
            role_msg = b"role:agent"
            self.socket.sendto(role_msg, (self.host, self.port))
            self._waiting_for_role_confirmation = True
            
            # 等待確認 (最多等待5秒)
            start_time = time.time()
            while self._waiting_for_role_confirmation and (time.time() - start_time) < 5.0:
                time.sleep(0.1)
            
            if self._role_registered:
                print("✅ 角色註冊成功")
                return True
            else:
                print("❌ 角色註冊超時")
                return False
                
        except Exception as e:
            print(f"❌ 角色註冊失敗: {e}")
            return False
        
    def _receive_loop(self):
        """接收訊息循環"""
        while self.running:
            try:
                if self.socket:
                    data, addr = self.socket.recvfrom(65536)  # 最大 64KB
                    
                    # 處理角色註冊確認
                    if self._waiting_for_role_confirmation:
                        message_str = data.decode('utf-8', errors='ignore')
                        if message_str == "ok:agent":
                            self._role_registered = True
                            self._waiting_for_role_confirmation = False
                            print("✅ 收到角色註冊確認: ok:agent")
                            continue
                    
                    # 只有在角色註冊成功後才處理遊戲訊息
                    if self._role_registered and data and self.on_message_callback:
                        self.on_message_callback(data)
                        
            except socket.timeout:
                # 超時是正常的，繼續循環
                continue
            except Exception as e:
                if self.running:  # 只有在運行時才報告錯誤
                    print(f"❌ UDP 接收錯誤: {e}")
                    if self.on_error_callback:
                        self.on_error_callback(e)
                break
        
        print("🔄 UDP 接收循環結束")
        
    def send_message(self, message_data: bytes):
        """發送訊息"""
        if not self._role_registered:
            print("⚠️ 角色未註冊，無法發送遊戲訊息")
            return
            
        if self.socket and self.running:
            try:
                self.socket.sendto(message_data, (self.host, self.port))
            except Exception as e:
                print(f"❌ Failed to send UDP message: {e}")
                if self.on_error_callback:
                    self.on_error_callback(e)
                
    def close(self):
        """關閉連線"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
            
        if self.on_close_callback:
            self.on_close_callback()


# 為了保持向後相容性，提供 UDPSocketManager 的別名
WebSocketManager = UDPManager
