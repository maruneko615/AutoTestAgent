#!/usr/bin/env python3
import asyncio
import socket
import time
import random
import sys
from ProtoSchema.GameFlowData_pb2 import GameFlowData
from ProtoSchema.InputCommand_pb2 import InputCommand

class AutoTestAgent:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8587
        self.socket = None
        self.role_registered = False
        self.game_states = ['Flow1', 'Flow2', 'Flow3', 'Flow4', 'Flow5', 'Flow6']
        self.keys = ['Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7']
        self.log_file = open('AutoTestAgent.log', 'w', encoding='utf-8')

    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_file.write(log_msg + '\n')
        self.log_file.flush()

    def create_input_command(self, key):
        cmd = InputCommand()
        cmd.key_inputs.append(key)
        cmd.is_key_down = True
        cmd.timestamp = int(time.time() * 1000)
        return cmd.SerializeToString()

    def process_game_data(self, data):
        try:
            game_data = GameFlowData()
            game_data.ParseFromString(data)

            self.log(f"接收 GameFlowData: state={game_data.current_flow_state}")
            self.log("=" * 50)

            random_key = random.choice(self.keys)
            input_cmd = self.create_input_command(random_key)

            self.socket.sendto(input_cmd, (self.host, self.port))
            self.log(f"發送 InputCommand: key={random_key}")
            self.log("=" * 50)

        except Exception as e:
            self.log(f"處理錯誤: {e}")

    async def handle_messages(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(4096)

                if not self.role_registered:
                    message = data.decode('utf-8')
                    if message == "ok:agent":
                        self.role_registered = True
                        self.log("角色註冊成功")
                    continue

                self.process_game_data(data)

            except Exception as e:
                self.log(f"接收錯誤: {e}")
                await asyncio.sleep(0.1)

    async def register_role(self):
        while not self.role_registered:
            try:
                self.socket.sendto("role:agent".encode('utf-8'), (self.host, self.port))
                self.log("發送角色註冊")
                await asyncio.sleep(1)
            except Exception as e:
                self.log(f"註冊錯誤: {e}")
                await asyncio.sleep(1)

    async def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.log(f"UDP Socket 已建立: {self.host}:{self.port}")

            await asyncio.gather(
                self.register_role(),
                self.handle_messages()
            )

        except KeyboardInterrupt:
            self.log("程式中斷")
        except Exception as e:
            self.log(f"運行錯誤: {e}")
        finally:
            if self.socket:
                self.socket.close()
            self.log_file.close()

if __name__ == "__main__":
    agent = AutoTestAgent()
    asyncio.run(agent.run())


