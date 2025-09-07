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
        """建構 Q CLI 提示詞"""
        prompt = f"""只需要生成純Python的可執行的程式碼，不要任何說明文字或格式化。

根據用戶指令和遊戲配置，修改 AutoTestAgent 生成定制化版本。

用戶指令: {user_command}

遊戲配置 (GameSetting.md):
{game_setting_content}

基礎 AutoTestAgent 程式碼:
{base_agent_content}

請分析用戶指令，理解需要在哪個遊戲狀態下執行什麼操作，然後修改 AutoTestAgent 的邏輯：

1. 在檔案開頭加上定制化指令註解
2. 修改日誌檔名為 AutoTestAgent_Custom.log
3. 在 __init__ 方法中記錄定制化指令
4. 根據用戶指令修改 send_random_input 方法的邏輯
5. 確保在指定的遊戲狀態下執行用戶要求的操作

只輸出完整的 Python 程式碼，不要任何說明文字或markdown格式。
不要使用 ```python 或 ``` 標記。
直接從 #!/usr/bin/env python3 開始輸出。"""
        
        return prompt
    
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
                
                # 調試：記錄原始輸出的前100個字符
                raw_preview = result.stdout[:100].replace('\n', '\\n')
                self.log(f"🔍 原始輸出預覽: {raw_preview}")
                
                # 直接使用原始輸出
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
        """從 Q CLI 輸出中提取純程式碼"""
        # 移除 ANSI 顏色代碼
        clean_output = self._remove_ansi_codes(output)
        
        # 強化 WSL 格式檢測：檢查是否每個字符都分行
        lines = clean_output.split('\n')
        if len(lines) > 20:
            # 檢查前20行是否都是單字符或很短
            single_char_count = sum(1 for line in lines[:20] if len(line.strip()) <= 2)
            if single_char_count >= 15:  # 如果大部分都是單字符，認為是 WSL 格式問題
                self.log("🔧 檢測到 WSL 格式問題，重組內容...")
                # 重組所有非空行
                rejoined = ''.join(line.strip() for line in lines if line.strip())
                clean_output = rejoined
                self.log(f"🔧 重組後內容預覽: {clean_output[:100]}")
        
        # 如果已經是純程式碼，直接返回
        if clean_output.strip().startswith('#!/usr/bin/env python3'):
            return clean_output.strip()
        
        # 嘗試提取 ```python 程式碼區塊
        if '```python' in clean_output:
            start_marker = '```python'
            end_marker = '```'
            start_idx = clean_output.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = clean_output.find(end_marker, start_idx)
                if end_idx != -1:
                    code_block = clean_output[start_idx:end_idx].strip()
                    if code_block and ('#!/usr/bin/env python3' in code_block or 'import' in code_block[:200]):
                        return code_block
        
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
        
        # 需要提取程式碼來修復 WSL 格式問題
        custom_code = self.extract_python_code(qcli_output)
        
        # 暫時跳過驗證，直接儲存
        # if not self._validate_generated_code(custom_code):
        #     self.log("❌ 生成的程式碼驗證失敗")
        #     return False
        
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
