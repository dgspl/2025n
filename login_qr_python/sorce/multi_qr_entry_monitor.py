import serial
import threading
import json
import time
import datetime
from db_handler import (
    get_connection,
    find_event_participant_by_query,
    get_last_entry_type,
    get_first_checked_in,
    insert_entry_log,
)

CONFIG_PATH = 'device_config.json'

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_query_param(qr_text):
    marker = "dn25:"
    idx = qr_text.find(marker)
    if idx == -1:
        return None
    return qr_text[idx:].strip()

def process_entry(conn, query_param, entry_type):
    ep = find_event_participant_by_query(conn, query_param)
    if ep is None:
        print(f"ERROR: No event participant found for query param: {query_param}")
        return False
    ep_id, user_id, event_id = ep

    last_entry = get_last_entry_type(conn, user_id, event_id)
    if last_entry == entry_type:
        print(f"ERROR: user_id={user_id} consecutive {entry_type} detected.")
        return False

    checked_in = None
    if entry_type == 'in':
        first_checked = get_first_checked_in(conn, user_id, event_id)
        if first_checked is None:
            checked_in = datetime.datetime.now()

    scanned_at = datetime.datetime.now()
    insert_entry_log(conn, user_id, event_id, entry_type, scanned_at, checked_in)
    print(f"Logged {entry_type} for user_id={user_id}, event_id={event_id} at {scanned_at}")
    return True

def reader_thread(com_port, role):
    try:
        ser = serial.Serial(com_port, 9600, timeout=1)
        print(f"{com_port} opened for {role} processing.")
    except Exception as e:
        print(f"Failed to open {com_port}: {e}")
        return

    conn = get_connection()

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                time.sleep(0.1)
                continue
            print(f"{com_port} read: {line}")

            query_param = extract_query_param(line)
            if query_param is None:
                print(f"Invalid QR code format from {com_port}: {line}")
                continue

            if role in ['entry', 'reentry']:
                etype = 'in'
            elif role == 'exit':
                etype = 'out'
            else:
                etype = 'unknown'

            process_entry(conn, query_param, etype)

        except Exception as e:
            print(f"Error in thread {com_port}: {e}")
            time.sleep(1)

def main():
    config = load_config()
    readers = config.get('readers', {})
    threads = []

    for com_port, role in readers.items():
        t = threading.Thread(target=reader_thread, args=(com_port, role), daemon=True)
        t.start()
        threads.append(t)

    print("All reader threads started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
