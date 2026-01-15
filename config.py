"""
Jetson Nano 顔追尾カメラシステム - 設定ファイル
"""

from pathlib import Path

# =============================================================================
# パス設定
# =============================================================================
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"

# =============================================================================
# カメラ設定
# =============================================================================
CAMERA_WIDTH: int = 640
CAMERA_HEIGHT: int = 480
CAMERA_FPS: int = 30

# CSIカメラ用GStreamerパイプライン
GSTREAMER_PIPELINE: str = (
    f"nvarguscamerasrc ! "
    f"video/x-raw(memory:NVMM), width={CAMERA_WIDTH}, height={CAMERA_HEIGHT}, "
    f"format=(string)NV12, framerate={CAMERA_FPS}/1 ! "
    f"nvvidconv flip-method=0 ! "
    f"video/x-raw, width={CAMERA_WIDTH}, height={CAMERA_HEIGHT}, format=(string)BGRx ! "
    f"videoconvert ! "
    f"video/x-raw, format=(string)BGR ! appsink"
)

# =============================================================================
# サーボ設定
# =============================================================================
# PWMピン (Jetson Nano GPIO)
SERVO_PAN_PIN: int = 33  # 水平方向 (左右)
SERVO_TILT_PIN: int = 32  # 垂直方向 (上下)

# サーボ角度制限
SERVO_PAN_MIN: int = 0
SERVO_PAN_MAX: int = 180
SERVO_PAN_CENTER: int = 90

SERVO_TILT_MIN: int = 30  # 下向き制限
SERVO_TILT_MAX: int = 150  # 上向き制限
SERVO_TILT_CENTER: int = 90

# PWM設定
PWM_FREQUENCY: int = 50  # Hz (標準的なサーボは50Hz)

# =============================================================================
# 追尾設定
# =============================================================================
# PID制御パラメータ
PID_KP: float = 0.5  # 比例ゲイン
PID_KI: float = 0.0  # 積分ゲイン
PID_KD: float = 0.1  # 微分ゲイン

# デッドゾーン（この範囲内では動作しない）
DEADZONE_X: int = 30  # ピクセル
DEADZONE_Y: int = 30  # ピクセル

# スムージング係数 (0.0〜1.0, 小さいほど滑らか)
SMOOTHING_FACTOR: float = 0.3

# =============================================================================
# 顔検出設定
# =============================================================================
# 検出モデルパス
FACE_CASCADE_PATH: str = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

# 検出パラメータ
DETECTION_SCALE_FACTOR: float = 1.1
DETECTION_MIN_NEIGHBORS: int = 5
DETECTION_MIN_SIZE: tuple[int, int] = (30, 30)
