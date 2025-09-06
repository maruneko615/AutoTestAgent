"""
統計和監控模組
負責收集和報告測試統計資訊
"""

import time
from typing import Dict, Any

class StatisticsManager:
    def __init__(self):
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'start_time': None,
            'key_presses': {},
            'state_transitions': {},
            'target_achievements': {},
            'selection_attempts': {},
            'current_targets': {}
        }
        
    def start_session(self):
        """開始統計會話"""
        self.stats['start_time'] = time.time()
        print("📊 Statistics session started")
        
    def end_session(self):
        """結束統計會話"""
        if self.stats['start_time']:
            self._print_final_stats()
            
    def record_input_sent(self):
        """記錄發送的輸入"""
        self.stats['messages_sent'] += 1
        
    def record_message_received(self):
        """記錄接收的訊息"""
        self.stats['messages_received'] += 1
        
    def record_key_press(self, key_type: int):
        """記錄按鍵按下"""
        if key_type not in self.stats['key_presses']:
            self.stats['key_presses'][key_type] = 0
        self.stats['key_presses'][key_type] += 1
        
    def record_state_transition(self, from_state: int, to_state: int):
        """記錄狀態轉換"""
        transition_key = f"{from_state}->{to_state}"
        if transition_key not in self.stats['state_transitions']:
            self.stats['state_transitions'][transition_key] = 0
        self.stats['state_transitions'][transition_key] += 1
        
    def record_target_achievement(self, target_type: str, achieved: bool):
        """記錄目標達成"""
        if target_type not in self.stats['target_achievements']:
            self.stats['target_achievements'][target_type] = {'achieved': 0, 'attempts': 0}
        
        self.stats['target_achievements'][target_type]['attempts'] += 1
        if achieved:
            self.stats['target_achievements'][target_type]['achieved'] += 1
            
    def record_selection_attempt(self, state: int, field_name: str, current_value: Any, target_value: Any):
        """記錄選擇嘗試"""
        key = f"{state}_{field_name}"
        if key not in self.stats['selection_attempts']:
            self.stats['selection_attempts'][key] = {
                'attempts': 0,
                'target_value': target_value,
                'last_value': None
            }
            
        self.stats['selection_attempts'][key]['attempts'] += 1
        self.stats['selection_attempts'][key]['last_value'] = current_value
        
    def set_current_targets(self, targets: Dict[str, Any]):
        """設定當前目標"""
        self.stats['current_targets'] = targets.copy()
        
    def print_stats(self):
        """打印當前統計資訊"""
        if not self.stats['start_time']:
            return
            
        elapsed = time.time() - self.stats['start_time']
        sent_rate = self.stats['messages_sent'] / elapsed if elapsed > 0 else 0
        recv_rate = self.stats['messages_received'] / elapsed if elapsed > 0 else 0
        
        print(f"\n📊 === Agent Statistics (Running: {elapsed:.1f}s) ===")
        print(f"📤 Messages sent: {self.stats['messages_sent']} ({sent_rate:.1f}/s)")
        print(f"📥 Messages received: {self.stats['messages_received']} ({recv_rate:.1f}/s)")
        
        # 顯示當前目標
        if self.stats['current_targets']:
            print(f"🎯 Current targets:")
            for target_type, target_value in self.stats['current_targets'].items():
                print(f"   {target_type}: {target_value}")
                
        # 顯示按鍵統計
        if self.stats['key_presses']:
            print("🎮 Key press statistics:")
            for key_type, count in self.stats['key_presses'].items():
                print(f"   Key {key_type}: {count}")
                
        # 顯示選擇嘗試統計
        if self.stats['selection_attempts']:
            print("🔍 Selection attempts:")
            for key, data in self.stats['selection_attempts'].items():
                progress = f"Current: {data['last_value']}, Target: {data['target_value']}"
                print(f"   {key}: {data['attempts']} attempts ({progress})")
                
        # 顯示目標達成統計
        if self.stats['target_achievements']:
            print("🏆 Target achievements:")
            for target_type, data in self.stats['target_achievements'].items():
                success_rate = (data['achieved'] / data['attempts'] * 100) if data['attempts'] > 0 else 0
                print(f"   {target_type}: {data['achieved']}/{data['attempts']} ({success_rate:.1f}%)")
                
    def _print_final_stats(self):
        """打印最終統計資訊"""
        if not self.stats['start_time']:
            return
            
        elapsed = time.time() - self.stats['start_time']
        print(f"\n🏁 === Final Statistics ===")
        print(f"⏱️  Total runtime: {elapsed:.2f} seconds")
        print(f"📤 Total messages sent: {self.stats['messages_sent']}")
        print(f"📥 Total messages received: {self.stats['messages_received']}")
        
        if elapsed > 0:
            print(f"📊 Average send rate: {self.stats['messages_sent']/elapsed:.2f} msg/s")
            print(f"📊 Average receive rate: {self.stats['messages_received']/elapsed:.2f} msg/s")
            
        # 最終目標達成報告
        if self.stats['target_achievements']:
            print(f"🏆 Final target achievement report:")
            for target_type, data in self.stats['target_achievements'].items():
                success_rate = (data['achieved'] / data['attempts'] * 100) if data['attempts'] > 0 else 0
                print(f"   {target_type}: {data['achieved']}/{data['attempts']} ({success_rate:.1f}%)")
