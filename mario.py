#!/usr/bin/env python3
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(0.5)

# スーパーマリオブラザーズ ゴールファンファーレ
# ソソソ ミーソー シーラーソー
notes = [
    (0, 784, 150),    # G5
    (180, 784, 150),  # G5
    (180, 784, 150),  # G5
    (250, 659, 300),  # E5
    (350, 784, 300),  # G5
    (400, 988, 300),  # B5
    (400, 880, 300),  # A5
    (400, 784, 500),  # G5
]

for wait, freq, dur in notes:
    if wait > 0:
        time.sleep(wait / 1000)
    ser.write(f'F{freq}D{dur}\n'.encode())
    time.sleep(dur / 1000)

ser.close()
print("Done!")
