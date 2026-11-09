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

スーパーマリオブラザーズのゴールファンファーレが鳴る。デバイスは `a.sh` と同じく
`$BEEP_DEV` → `/dev/beeper` → by-id 名 → `/dev/ttyUSB0` の順で最初に見つかったもの。

## ★ 踏みやすい罠 — シリアルを開くと Arduino がリセットされる

Arduino は **DTR が落ちるとリセットがかかる**。素直に書くと、音符を1つ送るたびに
ポートを開閉してボードが再起動し、**曲の合間に起動音（PC-98 風の2音）が挟まる**。

`a.sh` はこう避けている:

```bash
stty -F "$DEV" 9600 raw -echo -hupcl   # -hupcl: close で DTR を落とさない
exec 3<>"$DEV"                          # fd を開いたまま最後まで保持する
```

`mario.py` は開いた直後に termios で HUPCL を下ろす（`-hupcl` と同じ）。
起動を待つ処理は置いていない＝2026-10-11 に durandal 上の基板で、HUPCL を立てて開き直しても
DTR を明示的に 0.25 秒落としても、起動音は鳴らず `BEEPER READY` も読めなかったため
（この基板では DTR でリセットがかからなかった。別の Nano では要確認）。

## 基板が LGT8F328P の場合（2026-11-10 に判明）

2枚目の基板のチップは **LGT8F328P**（LogicGreen・ATmega328P の互換品）だった。1枚目（sis1 に挿してある物）もたぶん同じ。

- **クロックを設定しないプログラムだと既定の 4MHz で走る。**`platformio.ini` の `f_cpu = 4000000L` は（たぶん）このため。この設定のビルドで 9600 の命令が通り、音も鳴ることを確認した
- **DTR ではリセットしない。**`pio run -t upload` はそのままでは `not in sync` で失敗する
- ブートローダは **57600**。書き込みは、avrdude を回しながら**リセットボタンを短く押してすぐ離す**（押しっぱなしだとチップが止まったまま）。呼びかけの窓を広げると合わせやすい:
  ```
  avrdude -p m328p -c arduino -P /dev/ttyUSB0 -b 57600 -x attempts=10 -F -D -U flash:w:.pio/build/nanoatmega328/firmware.hex:i
  ```
  （`-F` はチップの照合を飛ばす。返ってくる署名は `0x1e950f` で m328p と同じ）
- 未解決: 基板から PC への返事（`BEEPER READY` / `OK …`）が読めなかった。PC から基板への命令は通る＝鳴らすだけなら困らない
- 青い LED は D13（「L」）。今のファームでは使っていない
- 充電専用の USB ケーブルだと `/dev/ttyUSB*` が出てこない（CH340 が見えない）。最初に疑う

## ライセンス

MIT License — [LICENSE](LICENSE) を参照。
