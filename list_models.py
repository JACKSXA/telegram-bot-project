#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""列出可用的 Gemini 模型"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# 加载环境变量
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# 配置API
genai.configure(api_key=GOOGLE_API_KEY)

print("正在查询可用的模型...")
print("=" * 50)

try:
    models = genai.list_models()
    print(f"\n找到 {len(list(models))} 个模型：\n")
    
    for model in genai.list_models():
        print(f"模型名称: {model.name}")
        print(f"  支持的方法: {model.supported_generation_methods}")
        print()
        
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")

