#!/bin/bash
# ラーファーミファミー (beeper firmware / F<freq>D<dur> 形式)
set -u
DEV=${BEEP_DEV:-/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0}

# ポートは最初に一度だけ開いて最後まで保持する。
# -hupcl が無いと音符ごとの close で DTR が落ちて Arduino がリセットし、
# 合間に PC-98 風の起動音が挟まってしまう。
stty -F "$DEV" 9600 raw -echo -hupcl || exit 1
exec 3<>"$DEV" || { echo "a.sh: $DEV を開けない (dialout?)" >&2; exit 1; }
trap 'exec 3>&-' EXIT

send() {
  printf 'F%sD%s\n' "$1" "$2" >&3
  sleep "$(awk "BEGIN{print $2/1000}")"
}

# ラーファーミファミー
send 440 150
send 440 50
send 349 150
send 349 50
send 330 150
send 349 100
send 330 150
send 330 50

# ソーファーミファミド
send 392 150
send 392 50
send 349 150
send 349 50
send 330 150
send 349 100
send 330 100
send 262 150
