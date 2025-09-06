# -*- coding: utf-8 -*-
"""
ProtoSchema 初始化檔案
自動設定 protobuf 環境變數以解決版本相容性問題
"""

import os

# 設定 protobuf 環境變數（在導入 pb2 檔案之前）
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
