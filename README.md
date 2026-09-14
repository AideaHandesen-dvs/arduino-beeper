# arduino-beeper

**PC にブザーを1個生やすための、Arduino Nano の周辺機器。**
USB シリアルに `F<周波数>D<長さ>` と書き込むと、その音が鳴る。それだけ。

WiFi も時計も持たない。PC 側のスクリプトが「いつ鳴らすか」を決め、こいつは「鳴らす」だけをやる。
監視の警報、長いビルドの完了通知、そういう用途に向く。

## 構成

```
PC ──USB(9600 8N1)── Arduino Nano ──D9── 圧電ブザー
```

| | |
|---|---|
| ボード | Arduino Nano (ATmega328) |
| ブザー | D9 (`tone()` で駆動) |
| ビルド | PlatformIO / `env:nanoatmega328` |
| ボーレート | 9600 |

`setup()` で D6 を OUTPUT・LOW にしている（ブザーの片脚を隣のピンに挿す配線に対応するため）。
`platformio.ini` の `board_build.f_cpu = 4000000L` は 4MHz 動作のボード向けの指定。
16MHz の素の Nano に載せるならここを `16000000L` に直すこと（音程とボーレートがずれる）。

## シリアルプロトコル

1行1コマンド。改行（`\n` または `\r`）で確定する。

```
F440D150     ←  440Hz を 150ms 鳴らせ
OK 440Hz 150ms
```

- `F` と `D` は順不同、間に何が挟まっていてもよい（`strchr` で拾っている）
- どちらかが 0 以下、または欠けていると `ERR` を返す
- 受け付けるのは1行31文字まで
- 電源投入時に `BEEPER READY` を返し、**PC-98 風の起動音**（2000Hz → 4000Hz）が鳴る

## 鳴らす側

### `a.sh` — シェルだけで鳴らす

```bash
BEEP_DEV=/dev/ttyUSB0 ./a.sh
```

既定のデバイスは `/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0`（CH340 の Nano）。
`by-id` を使うのは、`/dev/ttyUSB0` の番号が挿す順で入れ替わるため。

### `mario.py` — pyserial 版

```bash
pip install pyserial
./mario.py
```

スーパーマリオブラザーズのゴールファンファーレが鳴る（`/dev/ttyUSB0` 決め打ち）。

## ★ 踏みやすい罠 — シリアルを開くと Arduino がリセットされる

Arduino は **DTR が落ちるとリセットがかかる**。素直に書くと、音符を1つ送るたびに
ポートを開閉してボードが再起動し、**曲の合間に起動音（PC-98 風の2音）が挟まる**。

`a.sh` はこう避けている:

```bash
stty -F "$DEV" 9600 raw -echo -hupcl   # -hupcl: close で DTR を落とさない
exec 3<>"$DEV"                          # fd を開いたまま最後まで保持する
```

`mario.py` 側は `serial.Serial()` の直後に `time.sleep(0.5)` を置いて、
起動が終わるのを待ってから最初の音を送っている。
（より強く殺すなら `serial.Serial(..., dsrdtr=None, rtscts=False)` で開いて
`ser.dtr = False` / `ser.rts = False` を立ててから 1.5 秒待つ）

## ライセンス

未設定。
