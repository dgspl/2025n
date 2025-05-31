import serial.tools.list_ports

def detect_readers():
    """
    接続されたリーダー一覧を取得（COMポートで識別）
    """
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(f"デバイス: {p.device}, 説明: {p.description}, ハードウェアID: {p.hwid}")

# 実行して確認する
detect_readers()
