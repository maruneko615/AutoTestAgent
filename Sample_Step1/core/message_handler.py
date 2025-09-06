"""
Protobuf 訊息處理模組
負責解析和處理接收到的遊戲數據
"""

import sys
import os

# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import GameFlowData_pb2 as GameFlowData
except ImportError as e:
    print(f"✗ Failed to import GameFlowData_pb2: {e}")

class MessageHandler:
    def __init__(self):  # TODO: 🔧 移除 proto_analyzer 參數，改用固定 Proto 結構
        self.last_game_data = None
        # TODO: 🔧 移除 proto_analyzer，直接使用 GameFlowData_pb2 結構
        
    def parse_message(self, message: bytes):
        """解析接收到的訊息"""
        try:
            # 嘗試解析為GameFlowData
            game_data = GameFlowData.GameFlowData()
            game_data.ParseFromString(message)
            
            # 顯示解析結果
            self._display_game_data(game_data)
            
            self.last_game_data = game_data
            return game_data
            
        except Exception as e:
            print(f"❌ Protobuf 解析失敗: {e}")
            print(f"📨 Received message (length: {len(message)} bytes)")
            return None
            
    def _display_game_data(self, game_data):
        """顯示遊戲數據"""
        print(f"////////////////////////////////////////")
        print(f"✅ Protobuf 解析成功！")
        print(f"📊 GameFlowData 內容:")
        
        # 動態解析所有欄位
        if hasattr(game_data, 'DESCRIPTOR'):
            print(f"🔍 接收遊戲端資訊:")
            for field_descriptor in game_data.DESCRIPTOR.fields:
                field_name = field_descriptor.name
                field_value = getattr(game_data, field_name)
                
                # 嘗試顯示更有意義的資訊
                display_value = self._format_field_value(field_descriptor, field_value)
                print(f"  📋 {field_name}: {display_value}")
                
    def _format_field_value(self, field_descriptor, field_value):
        """格式化欄位值顯示"""
        try:
            # 如果是枚舉類型，顯示名稱
            if field_descriptor.type == field_descriptor.TYPE_ENUM:
                enum_type = field_descriptor.enum_type
                if enum_type:
                    for enum_value in enum_type.values:
                        if enum_value.number == field_value:
                            return f"{enum_value.name} ({field_value})"
                            
            # 如果是列表，格式化每個元素
            elif isinstance(field_value, list) and len(field_value) > 0:
                display_items = []
                for item in field_value:
                    if hasattr(item, '__class__') and hasattr(item.__class__, '__name__'):
                        display_items.append(f"{item} ({item.__class__.__name__})")
                    else:
                        display_items.append(str(item))
                return f"[{', '.join(display_items)}]"
                
            return str(field_value)
            
        except Exception:
            return str(field_value)
        
    def get_field_value(self, field_name: str):
        """獲取指定欄位的值"""
        if self.last_game_data and hasattr(self.last_game_data, field_name):
            return getattr(self.last_game_data, field_name)
        return None
