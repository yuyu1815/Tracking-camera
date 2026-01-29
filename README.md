# Jetson Nano 顔追尾カメラシステム

CSIカメラで検出した顔を自動追尾するパン・チルト機構

## セットアップ

### uv を使用（推奨）

```bash
# uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存パッケージのインストール
uv sync

# 開発用依存パッケージも含める場合
uv sync --extra dev
```

## 開発

```bash
# Linter & Formatter
uv run ruff check .
uv run ruff format .

# 型チェック
uv run mypy src/

# テスト
uv run pytest

# pre-commitフックのインストール
uv run pre-commit install
```

## 実行

```bash
# サーボキャリブレーション
uv run python scripts/calibrate_servo.py

# カメラテスト
uv run python scripts/test_camera.py

# 顔追尾システム起動
uv run python src/main.py           # CSIカメラ
uv run python src/main.py --usb     # USBカメラ
```

## ハードウェア接続

```
Jetson Nano GPIO
├── Pin 33 (PWM0) → サーボ Pan (信号線)
├── Pin 32 (PWM1) → サーボ Tilt (信号線)
├── Pin 2  (5V)   → サーボ電源 (+)
└── Pin 6  (GND)  → サーボ電源 (-)
```

## 必要部品

- Jetson Nano Developer Kit
- CSIカメラ (IMX219等)
- SG90 サーボモーター x2
- パン・チルトブラケット
- ジャンパー線
