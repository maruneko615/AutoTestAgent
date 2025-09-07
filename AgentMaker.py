#!/usr/bin/env python3
"""
AgentMaker - 使用 Q CLI 生成 AutoTestAgent 的工具
根據 GameSetting.md 和 Protobuf Schema 生成專屬的遊戲控制程式
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class AgentMaker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.game_setting_path = self.project_root / "GameSetting" / "AutoTest_Game_Setting.md"
        self.proto_schema_path = self.project_root / "ProtoSchema"
        self.log_file = self.project_root / "AgentMakerLog.txt"
        
        # 功能需求規格要求的輸入文件
        self.required_files = {
            "GameSetting.md": self.game_setting_path,
            "GameFlowData.proto": self.proto_schema_path / "GameFlowData.proto",
            "GameFlowData_pb2.py": self.proto_schema_path / "GameFlowData_pb2.py",
            "InputCommand.proto": self.proto_schema_path / "InputCommand.proto",
            "InputCommand_pb2.py": self.proto_schema_path / "InputCommand_pb2.py"
        }
        
    def validate_input_files(self):
        """驗證所有必要的輸入文件是否存在"""
        self.log("📋 檢查輸入文件...")
        missing_files = []
        
        for name, path in self.required_files.items():
            if path.exists():
                self.log(f"✅ {name}")
            else:
                self.log(f"❌ 缺少: {name}")
                missing_files.append(name)
        
        if missing_files:
            raise FileNotFoundError(f"缺少必要文件: {', '.join(missing_files)}")
        
        self.log("✅ 所有輸入文件檢查完成")
        
    def log(self, message):
        """同時輸出到控制台和日誌檔"""
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
        
    def analyze_game_setting(self):
        """分析 GameSetting.md 文件"""
        self.log("📋 分析 GameSetting.md...")
        
        if not self.game_setting_path.exists():
            raise FileNotFoundError(f"找不到 GameSetting 文件: {self.game_setting_path}")
            
        with open(self.game_setting_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取關鍵資訊
        game_config = {
            "states": self._extract_states(content),
            "keys": self._extract_keys(content),
            "udp_config": self._extract_udp_config(content)
        }
        
        self.log(f"✅ 發現 {len(game_config['states'])} 個遊戲狀態")
        self.log(f"✅ 發現 {len(game_config['keys'])} 個按鍵定義")
        
        return game_config
    
    def analyze_protobuf_schema(self):
        """分析 Protobuf Schema"""
        self.log("🔍 分析 Protobuf Schema...")
        
        proto_files = {
            "GameFlowData": self.proto_schema_path / "GameFlowData.proto",
            "InputCommand": self.proto_schema_path / "InputCommand.proto"
        }
        
        schema_info = {}
        for name, path in proto_files.items():
            if path.exists():
                schema_info[name] = self._analyze_proto_file(path)
                self.log(f"✅ 分析完成: {name}.proto")
            else:
                self.log(f"⚠️ 找不到: {path}")
                
        return schema_info
    
    def _get_q_command(self):
        """根據執行環境選擇適當的 Q CLI 命令"""
        import platform
        
        if platform.system() == "Windows":
            # Windows 環境，嘗試使用 WSL
            self.log("🪟 檢測到 Windows 環境，使用 WSL 執行 Q CLI...")
            return ["wsl", "-e", "bash", "-c"]
        else:
            # Linux/macOS 環境
            self.log("🐧 檢測到 Unix 環境，直接執行 Q CLI...")
            return ["q", "chat", "--no-interactive", "--trust-all-tools"]
    
    def generate_agent_code(self, game_config, schema_info):
        """使用 Q CLI 生成 AutoTestAgent 程式碼"""
        self.log("🤖 呼叫 Q CLI 生成程式碼...")
        
        # 準備 Q CLI 指令
        prompt = self._build_generation_prompt(game_config, schema_info)
        
        # 檢測執行環境並選擇適當的命令
        base_command = self._get_q_command()
        
        # 執行 Q CLI
        try:
            import platform
            if platform.system() == "Windows":
                # Windows + WSL 格式，設定正確的編碼
                full_command = f"q chat --no-interactive --trust-all-tools '{prompt}'"
                result = subprocess.run(
                    base_command + [full_command], 
                    capture_output=True, text=True, 
                    cwd=self.project_root,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                # Linux/macOS 格式
                result = subprocess.run(
                    base_command + [prompt], 
                    capture_output=True, text=True, 
                    cwd=self.project_root,
                    encoding='utf-8'
                )
            
            self.log(f"Q CLI 返回碼: {result.returncode}")
            if result.stdout:
                self.log(f"Q CLI 輸出長度: {len(result.stdout)} 字符")
            if result.stderr:
                self.log(f"Q CLI 錯誤: {result.stderr}")
            
            if result.returncode == 0 and result.stdout:
                self.log("✅ Q CLI 執行成功")
                # 提取純程式碼，移除 Q CLI 的格式化輸出
                clean_code = self._extract_code_from_output(result.stdout)
                if clean_code and len(clean_code.strip()) > 100:  # 檢查是否有實際程式碼內容
                    return clean_code
                else:
                    # 如果提取失敗，直接使用原始輸出（可能已經是純程式碼）
                    if result.stdout.strip().startswith('#!/usr/bin/env python3') or 'import' in result.stdout[:200]:
                        self.log("✅ 檢測到純程式碼輸出")
                        return result.stdout.strip()
                    else:
                        self.log("⚠️ 程式碼提取結果為空，使用原始輸出")
                        return result.stdout
            else:
                self.log(f"❌ Q CLI 執行失敗")
                self.log(f"返回碼: {result.returncode}")
                self.log(f"錯誤輸出: {result.stderr}")
                return None
                
        except Exception as e:
            self.log(f"❌ 執行 Q CLI 時發生異常: {e}")
            return None
    
    def _extract_states(self, content):
        """從內容中提取遊戲狀態"""
        states = []
        lines = content.split('\n')
        in_enum = False
        
        for line in lines:
            # 動態識別包含 "Flow" 或 "State" 的 enum
            if 'enum' in line and ('Flow' in line or 'State' in line):
                in_enum = True
                continue
            if in_enum and '}' in line:
                in_enum = False
                continue
            if in_enum and '=' in line:
                state_name = line.strip().split('=')[0].strip().rstrip(',')
                if state_name and not state_name.startswith('//'):
                    states.append(state_name)
                    
        return states
    
    def _extract_keys(self, content):
        """從內容中提取按鍵定義"""
        keys = []
        lines = content.split('\n')
        in_enum = False
        
        for line in lines:
            # 動態識別包含 "Key" 或 "Input" 的 enum
            if 'enum' in line and ('Key' in line or 'Input' in line):
                in_enum = True
                continue
            if in_enum and '}' in line:
                in_enum = False
                continue
            if in_enum and '=' in line:
                key_name = line.strip().split('=')[0].strip().rstrip(',')
                if key_name and not key_name.startswith('//'):
                    keys.append(key_name)
                    
        return keys
    
    def _extract_udp_config(self, content):
        """從內容中提取 UDP 配置"""
        lines = content.split('\n')
        config = {"host": "127.0.0.1", "port": 8587}  # 預設值
        
        for line in lines:
            line = line.strip()
            # 查找 UDP 相關配置
            if 'UDPSOCKET_URL' in line and '=' in line:
                url = line.split('=')[1].strip().strip('"\'')
                # 解析 udp://host:port 格式
                if url.startswith('udp://'):
                    host_port = url[6:]  # 移除 udp://
                    # 檢查是否為模板格式
                    if '[IP_ADDRESS]' in host_port or '[PORT]' in host_port:
                        print("⚠️ 發現模板格式的UDP配置，使用預設值")
                        continue
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                        try:
                            config["host"] = host
                            config["port"] = int(port)
                        except ValueError:
                            print(f"⚠️ 無效的端口號: {port}，使用預設值")
            elif 'UDP_HOST' in line and '=' in line:
                host = line.split('=')[1].strip().strip('"\'')
                if '[IP_ADDRESS]' not in host:
                    config["host"] = host
            elif 'UDP_PORT' in line and '=' in line:
                port_str = line.split('=')[1].strip().strip('"\'')
                if '[PORT]' not in port_str:
                    try:
                        config["port"] = int(port_str)
                    except ValueError:
                        print(f"⚠️ 無效的端口號: {port_str}，使用預設值")
                
        return config
    
    def _analyze_proto_file(self, proto_path):
        """分析單個 proto 文件"""
        with open(proto_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        info = {
            "enums": [],
            "messages": [],
            "input_keys": []  # 新增：提取輸入按鍵
        }
        
        lines = content.split('\n')
        in_input_key_enum = False
        
        for line in lines:
            line = line.strip()
            
            # 檢測枚舉定義
            if line.startswith('enum '):
                enum_name = line.split()[1]
                info["enums"].append(enum_name)
                # 檢查是否是輸入按鍵枚舉
                if 'InputKeyType' in enum_name:
                    in_input_key_enum = True
            elif line.startswith('message '):
                msg_name = line.split()[1]
                info["messages"].append(msg_name)
            elif line == '}':
                in_input_key_enum = False
            elif in_input_key_enum and '=' in line:
                # 提取按鍵名稱
                key_line = line.split('=')[0].strip()
                if key_line.startswith('INPUT_KEY_'):
                    info["input_keys"].append(key_line)
                
        return info
    
    def _extract_code_from_output(self, output):
        """從 Q CLI 輸出中提取純程式碼"""
        # 移除 ANSI 顏色代碼
        clean_output = self._remove_ansi_codes(output)
        
        # 如果已經是純程式碼，直接返回
        if clean_output.strip().startswith('#!/usr/bin/env python3'):
            return clean_output.strip()
        
        # 否則嘗試提取程式碼區塊
        lines = clean_output.split('\n')
        code_lines = []
        found_shebang = False
        
        for line in lines:
            # 找到 shebang 開始收集
            if line.strip().startswith('#!/usr/bin/env python3'):
                found_shebang = True
                code_lines.append(line.strip())
                continue
                
            # 如果已經開始收集，繼續收集非格式化行
            if found_shebang:
                # 跳過明顯的格式化行
                if any(marker in line for marker in ['🛠️', '●', '⋮', '[39m', '[0m', '> ']):
                    continue
                code_lines.append(line.rstrip())
        
        return '\n'.join(code_lines) if code_lines else clean_output.strip()
    
    def _validate_generated_code(self, code):
        """驗證生成的程式碼品質"""
        # 基本檢查
        if not code.strip():
            self.log("❌ 程式碼為空")
            return False
            
        # 檢查必要的導入
        required_imports = [
            'from ProtoSchema.GameFlowData_pb2 import GameFlowData',
            'from ProtoSchema.InputCommand_pb2 import InputCommand'
        ]
        
        for required in required_imports:
            if required not in code:
                self.log(f"❌ 缺少必要導入: {required}")
                return False
        
        # 檢查必要的類別 (放寬標準)
        if 'class AutoTestAgent' not in code:
            self.log("❌ 缺少 AutoTestAgent 類別")
            return False
        
        # 檢查是否包含格式化標記
        if any(marker in code for marker in ['[0m', '[39m', '🛠️', '●']):
            self.log("❌ 程式碼包含格式化標記")
            return False
            
        self.log("✅ 程式碼品質檢查通過")
        return True
    
    def _remove_ansi_codes(self, text):
        """移除 ANSI 顏色代碼"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _build_generation_prompt(self, game_config, schema_info):
        """建立 Q CLI 生成提示"""
        
        # 提取實際的按鍵列表
        input_keys = []
        if 'InputCommand' in schema_info:
            input_keys = schema_info['InputCommand'].get('input_keys', [])
        
        # 生成按鍵映射代碼
        key_mapping_code = "self.key_mapping = {\n"
        for key in input_keys[:8]:  # 限制前8個常用按鍵
            key_name = key.replace('INPUT_KEY_', '')
            key_mapping_code += f'            "{key_name}": EInputKeyType.{key},\n'
        key_mapping_code += "        }"
        
        # 生成可用按鍵列表
        available_keys = [key.replace('INPUT_KEY_', '') for key in input_keys[:5]]
        available_keys_str = str(available_keys)
        
        prompt = f"""只需要生成純Python程式碼，不要任何說明文字或格式化。

生成 AutoTestAgent.py，專門為Windows環境設計，具備持續監聽功能：

1. 必須包含路徑修正和Protobuf導入：
```python
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
    print(f"❌ 無法導入 Protobuf 模組: {{e}}")
    input("按 Enter 鍵結束...")
    sys.exit(1)
```

2. **動態按鍵映射**（重要）：
```python
# 按鍵映射 - 使用實際的 EInputKeyType 枚舉
{key_mapping_code}
```

3. **持續監聽機制**（重要）：
- 程式啟動後顯示 "🔄 等待遊戲連線..." 並持續嘗試連接
- 連線失敗時每5秒重試一次，不退出程式
- 連線成功後顯示 "✅ 遊戲連線成功，開始接收數據"
- 連線中斷時顯示 "❌ 遊戲連線中斷，5秒後重試..." 並自動重連
- 支援 Ctrl+C 優雅退出，顯示 "程式已停止"
- 使用 signal.signal(signal.SIGINT, signal_handler) 處理中斷

4. **核心架構**：
```python
class AutoTestAgent:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8587
        self.socket = None
        self.running = False
        self.connected = False
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        self.log("程式已停止")
        self.running = False
        sys.exit(0)
    
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
    
    def listen_loop(self):
        while self.running and self.connected:
            try:
                data, addr = self.socket.recvfrom(4096)
                self.process_game_data(data)
            except Exception as e:
                self.log(f"❌ 遊戲連線中斷: {{e}}")
                self.connected = False
                break
    
    def run(self):
        self.running = True
        while self.running:
            if self.connect_to_game():
                self.listen_loop()
```

5. **隨機按鍵選擇**：
使用可用按鍵列表: {available_keys_str}

6. 必須包含完整的日誌系統：
- 同時輸出到控制台和 AutoTestAgentLog.txt
- 每個重要操作都要記錄
- 包含時間戳記
- 使用 flush() 確保即時寫入
- **接收遊戲數據時必須記錄所有欄位**：
  ```python
  self.log(f"📥 接收遊戲數據:")
  self.log(f"   所有欄位: {{game_data}}")
  self.log(f"   狀態: {{game_data.current_flow_state}}")
  ```

7. 遊戲狀態：{game_config['states']}
8. 按鍵定義：{input_keys}
9. UDP配置：{game_config['udp_config']}

10. 必須包含：
- 路徑修正（在最開頭）
- 完整日誌系統（同時輸出到控制台和檔案）
- UDP通訊 + 角色註冊 ("role:agent" → "ok:agent")
- 持續監聽循環，連線失敗時自動重試
- 每個狀態的隨機輸入處理
- 信號處理機制支援 Ctrl+C 優雅退出
- main函數使用 try/except KeyboardInterrupt

只輸出完整的Python程式碼，從#!/usr/bin/env python3開始。"""
        return prompt
    
    def run(self):
        """執行 AgentMaker"""
        # 清空日誌檔
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("")
            
        self.log("🚀 啟動 AgentMaker...")
        
        try:
            # 0. 驗證輸入文件 (符合功能需求規格)
            self.validate_input_files()
            
            # 1. 分析配置
            game_config = self.analyze_game_setting()
            schema_info = self.analyze_protobuf_schema()
            
            # 2. 生成程式碼
            agent_code = self.generate_agent_code(game_config, schema_info)
            
            if agent_code:
                # 先儲存程式碼，再檢查品質
                output_path = self.project_root / "AutoTestAgent.py"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(agent_code)
                
                file_size = output_path.stat().st_size
                self.log(f"📄 程式碼已儲存: {output_path} ({file_size} bytes)")
                
                # 檢查程式碼品質
                if self._validate_generated_code(agent_code):
                    self.log("✅ AutoTestAgent 生成完成，品質檢查通過")
                else:
                    self.log("⚠️ AutoTestAgent 已生成，但品質檢查未通過")
            else:
                self.log("❌ 程式碼生成失敗")
                
        except Exception as e:
            self.log(f"❌ AgentMaker 執行失敗: {e}")
            sys.exit(1)

if __name__ == "__main__":
    maker = AgentMaker()
    maker.run()
    
    # 在 Windows 下保持視窗開啟
    input("\n按 Enter 鍵結束...")
