#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoTestBuilder - 定制化測試工具建置器
使用 Q CLI 根據用戶指令和 GameSetting.md 生成定制化的 AutoTestAgent
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

class AutoTestBuilder:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_agent_path = os.path.join(self.script_dir, "AutoTestAgent.py")
        self.output_path = os.path.join(self.script_dir, "AutoTestAgent_Custom.py")
        self.log_file = os.path.join(self.script_dir, "AutoTestBuilder.log")
        self.game_setting_path = os.path.join(self.script_dir, "GameSetting", "AutoTest_Game_Setting.md")
        
        # 清空日誌文件
        with open(self.log_file, 'w', encoding='utf-8') as f:
            pass
        
    def log(self, message):
        """記錄訊息到控制台和檔案"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
            f.flush()
    
    def load_game_setting(self):
        """載入 GameSetting.md 內容"""
        if not os.path.exists(self.game_setting_path):
            self.log(f"❌ 找不到遊戲配置文件: {self.game_setting_path}")
            return ""
            
        with open(self.game_setting_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_base_agent(self):
        """載入基礎 AutoTestAgent.py 內容"""
        if not os.path.exists(self.base_agent_path):
            self.log(f"❌ 找不到基礎 AutoTestAgent: {self.base_agent_path}")
            return ""
            
        with open(self.base_agent_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def build_qcli_prompt(self, user_command, game_setting_content, base_agent_content):
        """建構 Q CLI 提示詞 - 動態提取配置"""
        
        # 動態提取遊戲狀態
        states = self._extract_states(game_setting_content)
        
        # 動態提取按鍵定義
        keys = self._extract_keys(game_setting_content)
        
        # 動態提取 UDP 配置
        udp_config = self._extract_udp_config(game_setting_content)
        
        # 生成按鍵映射代碼
        key_mapping_code = "self.key_mapping = {\n"
        for key in keys[:8]:  # 限制前8個常用按鍵
            key_name = key.replace('INPUT_KEY_', '') if key.startswith('INPUT_KEY_') else key
            key_mapping_code += f'            "{key_name}": EInputKeyType.INPUT_KEY_{key_name},\n'
        key_mapping_code += "        }"
        
        # 生成可用按鍵列表
        available_keys = [key.replace('INPUT_KEY_', '') if key.startswith('INPUT_KEY_') else key for key in keys[:5]]
        available_keys_str = str(available_keys)
        
        prompt = f"""只需要生成純Python程式碼，不要任何說明文字或格式化。

根據用戶指令生成定制化的 AutoTestAgent.py，專門為Windows環境設計：

用戶指令: {user_command}

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

2. 動態按鍵映射：
```python
# 按鍵映射 - 使用實際的 EInputKeyType 枚舉
{key_mapping_code}
```

3. 定制化邏輯：
- 檔案開頭註解: # 定制化指令: {user_command}
- 日誌檔名: AutoTestAgent_Custom.log
- 根據用戶指令在特定遊戲狀態執行特定操作
- 其他狀態使用隨機輸入

4. 遊戲狀態：{states}
5. 按鍵定義：{keys}
6. UDP配置：{udp_config}
7. 可用按鍵：{available_keys_str}

8. 必須包含完整的：
- UDP通訊 + 角色註冊機制
- 持續監聽與自動重連
- 日誌系統（控制台+檔案）
- 信號處理支援 Ctrl+C

只輸出完整的Python程式碼，從#!/usr/bin/env python3開始。"""
        
        return prompt
    
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
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                        try:
                            config["host"] = host
                            config["port"] = int(port)
                        except ValueError:
                            pass
                
        return config
    
    def _get_q_command(self):
        """根據執行環境選擇適當的 Q CLI 命令"""
        import platform
        
        if platform.system() == "Windows":
            # Windows 環境，使用 WSL
            self.log("🪟 檢測到 Windows 環境，使用 WSL 執行 Q CLI...")
            return ["wsl", "-e", "bash", "-c"]
        else:
            # Linux/macOS 環境
            self.log("🐧 檢測到 Unix 環境，直接執行 Q CLI...")
            return ["q", "chat", "--no-interactive", "--trust-all-tools"]
    
    def call_qcli(self, prompt):
        """呼叫 Q CLI 生成程式碼"""
        try:
            self.log("🤖 呼叫 Q CLI 進行程式碼生成...")
            
            # 檢測執行環境並選擇適當的命令
            base_command = self._get_q_command()
            
            # 執行 Q CLI
            import platform
            if platform.system() == "Windows":
                # Windows + WSL 格式，設定正確的編碼
                full_command = f"q chat --no-interactive --trust-all-tools '{prompt}'"
                result = subprocess.run(
                    base_command + [full_command], 
                    capture_output=True, text=True, 
                    cwd=self.script_dir,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                # Linux/macOS 格式
                result = subprocess.run(
                    base_command + [prompt], 
                    capture_output=True, text=True, 
                    cwd=self.script_dir,
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
    
    def _remove_ansi_codes(self, text):
        """移除 ANSI 顏色代碼"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _extract_code_from_output(self, output):
        """從 Q CLI 輸出中提取純程式碼 - 強化 WSL 修復"""
        # 移除 ANSI 顏色代碼
        clean_output = self._remove_ansi_codes(output)
        
        # 檢測 WSL 格式問題：每個字符分行
        lines = clean_output.split('\n')
        if len(lines) > 100:  # 如果行數異常多
            # 檢查是否大部分行都是單字符
            single_char_lines = [line for line in lines if len(line.strip()) == 1]
            if len(single_char_lines) > len(lines) * 0.7:  # 70% 以上是單字符行
                self.log("🔧 檢測到嚴重的 WSL 格式問題，重組程式碼...")
                # 直接連接所有非空行
                rejoined = ''.join(line.strip() for line in lines if line.strip())
                # 在關鍵位置插入換行
                rejoined = rejoined.replace('#!/usr/bin/env python3', '#!/usr/bin/env python3\n')
                rejoined = rejoined.replace('# -*- coding: utf-8 -*-', '\n# -*- coding: utf-8 -*-\n')
                rejoined = rejoined.replace('import ', '\nimport ')
                rejoined = rejoined.replace('from ', '\nfrom ')
                rejoined = rejoined.replace('class ', '\n\nclass ')
                rejoined = rejoined.replace('def ', '\n    def ')
                rejoined = rejoined.replace('if __name__', '\n\nif __name__')
                clean_output = rejoined
                self.log(f"🔧 WSL 格式修復完成")
        
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
    
    def extract_python_code(self, qcli_output):
        """從 Q CLI 輸出中提取 Python 程式碼"""
        # 使用與 AgentMaker 相同的提取邏輯
        return self._extract_code_from_output(qcli_output)
    
    def _validate_generated_code(self, code):
        """驗證生成的程式碼品質"""
        # 基本檢查
        if not code.strip():
            self.log("❌ 程式碼為空")
            return False
            
        # 檢查是否包含必要的元素
        required_elements = ['#!/usr/bin/env python3', 'class AutoTestAgent', 'def __init__']
        for element in required_elements:
            if element not in code:
                self.log(f"❌ 程式碼缺少必要元素: {element}")
                return False
        
        # 語法檢查
        try:
            compile(code, '<string>', 'exec')
            self.log("✅ 程式碼語法檢查通過")
            return True
        except SyntaxError as e:
            self.log(f"❌ 程式碼語法錯誤: {e}")
            return False
        except Exception as e:
            self.log(f"❌ 程式碼編譯錯誤: {e}")
            return False
    
    def _clean_generated_code(self, code):
        """清理生成的程式碼，修復常見問題"""
        if not code:
            return code
            
        # 檢測並修復 WSL 格式問題（每個字符分行）
        lines = code.split('\n')
        if len(lines) > 50:  # 如果行數過多，可能是 WSL 格式問題
            # 檢查前20行是否大部分都是單字符
            single_char_count = sum(1 for line in lines[:20] if len(line.strip()) <= 2 and line.strip())
            if single_char_count >= 15:  # 如果大部分都是單字符
                self.log("🔧 檢測到 WSL 格式問題，重組程式碼...")
                # 重組所有非空行
                rejoined = ''.join(line.strip() for line in lines if line.strip())
                # 嘗試重新格式化為正常的 Python 程式碼
                code = self._reformat_python_code(rejoined)
                self.log(f"🔧 重組完成，程式碼長度: {len(code)}")
            
        # 移除開頭的 > 符號
        if code.startswith('> #!/usr/bin/env python3'):
            code = code[2:]  # 移除 "> "
            
        # 修復常見的語法錯誤
        code = code.replace('def init(self):', 'def __init__(self):')
        code = code.replace('self.log("="  50)', 'self.log("=" * 50)')
        code = code.replace('def sendinput_based_on_state', 'def send_input_based_on_state')
        code = code.replace('time.time()  1000', 'time.time() * 1000')
        code = code.replace('inputcommand', 'input_command')
        code = code.replace('if name == "__main__":', 'if __name__ == "__main__":')
        
        # 移除非 ASCII 字符（保留中文註解）
        lines = code.split('\n')
        clean_lines = []
        for line in lines:
            # 如果行包含註解且有中文，保留
            if '#' in line and any('\u4e00' <= char <= '\u9fff' for char in line):
                clean_lines.append(line)
            else:
                # 否則移除非 ASCII 控制字符
                clean_line = ''.join(char for char in line if ord(char) >= 32 or char in '\t\n\r')
                clean_lines.append(clean_line)
                
        return '\n'.join(clean_lines)
    
    def _reformat_python_code(self, joined_code):
        """重新格式化被 WSL 破壞的 Python 程式碼"""
        # 基本的 Python 關鍵字和結構
        keywords = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            'import ', 'from ', 'class ', 'def ', 'if ', 'else:', 'elif ', 'try:', 'except',
            'for ', 'while ', 'return ', 'self.', 'print(', '__init__', '__name__'
        ]
        
        result = []
        i = 0
        current_line = ""
        
        while i < len(joined_code):
            # 檢查是否匹配關鍵字
            matched = False
            for keyword in keywords:
                if joined_code[i:].startswith(keyword):
                    if current_line.strip():
                        result.append(current_line)
                        current_line = ""
                    current_line = keyword
                    i += len(keyword)
                    matched = True
                    break
            
            if not matched:
                current_line += joined_code[i]
                i += 1
                
            # 檢查是否應該換行
            if current_line.endswith(':') or current_line.endswith('"""') or len(current_line) > 80:
                result.append(current_line)
                current_line = ""
        
        if current_line.strip():
            result.append(current_line)
            
        return '\n'.join(result)
    
    def process_command(self, command):
        """統一的指令處理流程"""
        self.log(f"📋 接收指令: {command}")
        
        # 載入必要文件
        game_setting_content = self.load_game_setting()
        base_agent_content = self.load_base_agent()
        
        if not game_setting_content or not base_agent_content:
            self.log("❌ 無法載入必要文件")
            return False
        
        # 建構 Q CLI 提示詞
        prompt = self.build_qcli_prompt(command, game_setting_content, base_agent_content)
        
        # 呼叫 Q CLI
        qcli_output = self.call_qcli(prompt)
        if not qcli_output:
            return False
        
        # 提取程式碼
        custom_code = self.extract_python_code(qcli_output)
        
        # 清理程式碼
        custom_code = self._clean_generated_code(custom_code)
        
        # 驗證程式碼品質
        if not self._validate_generated_code(custom_code):
            self.log("⚠️ 程式碼驗證失敗，但仍會儲存")
        
        # 儲存定制化版本
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(custom_code)
            
        self.log(f"✅ 定制化 AutoTestAgent 已生成: {self.output_path}")
        return True
    
    def run_interactive(self):
        """互動式執行模式"""
        self.log("🚀 AutoTestBuilder 互動模式啟動")
        self.log("輸入自然語言指令，例如: '每次都選首爾'")
        
        try:
            command = input("\n請輸入指令: ").strip()
            
            if not command:
                self.log("❌ 未輸入指令")
                input("\n按 Enter 鍵結束...")
                return
                
            # 使用統一的處理流程
            if self.process_command(command):
                self.log("✅ 定制化測試工具建置完成")
            else:
                self.log("❌ 建置失敗")
                
            # 保持視窗開啟
            input("\n按 Enter 鍵結束...")
                        
        except KeyboardInterrupt:
            self.log("\n👋 使用者中斷，AutoTestBuilder 結束")
            input("\n按 Enter 鍵結束...")
        except Exception as e:
            self.log(f"❌ 執行錯誤: {e}")
            input("\n按 Enter 鍵結束...")

def main():
    parser = argparse.ArgumentParser(description='AutoTestBuilder - 定制化測試工具建置器')
    parser.add_argument('--command', help='自然語言測試指令')
    parser.add_argument('--interactive', action='store_true', help='互動模式')
    
    args = parser.parse_args()
    
    builder = AutoTestBuilder()
    
    if args.interactive or (not args.command and len(sys.argv) == 1):
        # 互動模式
        builder.run_interactive()
    elif args.command:
        # GitHub Action 模式 - 使用相同的處理流程
        builder.log("🚀 AutoTestBuilder GitHub Action 模式啟動")
        if builder.process_command(args.command):
            builder.log("✅ 定制化測試工具建置完成")
        else:
            builder.log("❌ 建置失敗")
            sys.exit(1)
    else:
        print("請使用 --interactive 或 --command 參數")
        parser.print_help()

if __name__ == "__main__":
    main()
