import sys
import os

# 現在のフォルダをPythonパスに追加
sys.path.insert(0, os.path.dirname(__file__))

# app.pyからFlaskアプリを読み込む
from app import app as application