#!/bin/bash
cd ~/Desktop/アプリ開発/QuantifyMe
source venv/bin/activate

# サーバーをバックグラウンドで起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# サーバーが起動するまで少し待つ
sleep 2

# ブラウザでダッシュボードを開く
open http://127.0.0.1:8000/dashboard

# フォアグラウンドのプロセスを待機(ターミナルを開いたままにする)
wait
