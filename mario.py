#!/usr/bin/env python3
import os
import termios
import time

import serial

# デバイスは上から順に最初に見つかったもの（~/bin/beep・a.sh と同じ並び）。
# CH340 は通し番号を持たないので、udev で名付けた /dev/beeper を最優先。
CANDIDATES = [
    os.environ.get('BEEP_DEV'),
    '/dev/beeper',
    '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0',
    '/dev/ttyUSB0',
]
dev = next((d for d in CANDIDATES if d and os.path.exists(d)), None)
if dev is None:
    raise SystemExit('mario.py: ブザー基板が見つからない（BEEP_DEV で指定できる）')

ser = serial.Serial(dev, 9600, timeout=0)

# HUPCL を下ろす＝この close で DTR を落とさない（a.sh の -hupcl と同じ）。
# 2026-10-11 に durandal の基板で試した限りでは、DTR を落としても起動音は鳴らず
# BEEPER READY も来なかった＝起動を待つ処理は置いていない。
attrs = termios.tcgetattr(ser.fd)
attrs[2] &= ~termios.HUPCL
termios.tcsetattr(ser.fd, termios.TCSANOW, attrs)

# スーパーマリオブラザーズ ゴールファンファーレ（旗のポール）
# ソドミソドミ ソーミー / ラ♭ドミ♭ラ♭ドミ♭ ラ♭ーミ♭ー / シ♭レファシ♭レファ シ♭ー シ♭シ♭シ♭ ドーー
# (待ち ms, 周波数 Hz, 長さ ms)。待ちは前の音が鳴り終わってから次を送るまで。
notes = [
    (0, 392, 100),    # G4
    (10, 523, 100),   # C5
    (10, 659, 100),   # E5
    (10, 784, 100),   # G5
    (10, 1047, 100),  # C6
    (10, 1319, 100),  # E6
    (10, 1568, 300),  # G6
    (30, 1319, 300),  # E6

    (30, 415, 100),   # Ab4
    (10, 523, 100),   # C5
    (10, 622, 100),   # Eb5
    (10, 831, 100),   # Ab5
    (10, 1047, 100),  # C6
    (10, 1245, 100),  # Eb6
    (10, 1661, 300),  # Ab6
    (30, 1245, 300),  # Eb6

    (30, 466, 100),   # Bb4
    (10, 587, 100),   # D5
    (10, 698, 100),   # F5
    (10, 932, 100),   # Bb5
    (10, 1175, 100),  # D6
    (10, 1397, 100),  # F6
    (10, 1865, 300),  # Bb6
    (30, 1865, 100),  # Bb6
    (10, 1865, 100),  # Bb6
    (10, 1865, 100),  # Bb6
    (10, 2093, 700),  # C7
]

for wait, freq, dur in notes:
    if wait > 0:
        time.sleep(wait / 1000)
    ser.write(f'F{freq}D{dur}\n'.encode())
    time.sleep(dur / 1000)

ser.close()
print("Done!")
