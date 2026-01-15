"""追尾ロジックモジュール - PID制御とスムージングで滑らかな追尾を実現."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import config

from src.logger import get_logger

if TYPE_CHECKING:
    from src.servo_controller import ServoController

logger = get_logger(__name__)


@dataclass
class TrackerStatus:
    """トラッカーの現在状態."""

    tracking: bool
    pan: float
    tilt: float
    lost_count: int


class PIDController:
    """PID制御器."""

    def __init__(
        self,
        kp: float | None = None,
        ki: float | None = None,
        kd: float | None = None,
    ) -> None:
        self.kp = kp if kp is not None else config.PID_KP
        self.ki = ki if ki is not None else config.PID_KI
        self.kd = kd if kd is not None else config.PID_KD

        self.prev_error: float = 0
        self.integral: float = 0

    def compute(self, error: float) -> float:
        """PID出力を計算.

        Args:
            error: 目標との誤差

        Returns:
            float: 制御出力
        """
        self.integral += error
        derivative = error - self.prev_error

        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        self.prev_error = error
        return output

    def reset(self) -> None:
        """状態をリセット."""
        self.prev_error = 0
        self.integral = 0


class FaceTracker:
    """顔追尾コントローラー."""

    def __init__(
        self,
        servo_controller: ServoController,
        frame_width: int,
        frame_height: int,
    ) -> None:
        """トラッカーを初期化.

        Args:
            servo_controller: ServoControllerインスタンス
            frame_width: 画面幅
            frame_height: 画面高さ
        """
        self.servo = servo_controller
        self.frame_width = frame_width
        self.frame_height = frame_height

        # 画面中心
        self.center_x = frame_width // 2
        self.center_y = frame_height // 2

        # PID制御器
        self.pid_pan = PIDController()
        self.pid_tilt = PIDController()

        # スムージング用
        self.smooth_pan: float = config.SERVO_PAN_CENTER
        self.smooth_tilt: float = config.SERVO_TILT_CENTER

        # 追跡状態
        self.tracking = False
        self.lost_count = 0
        self.lost_threshold = 30  # これ以上見失ったら中央に戻る

    def update(self, face_center: tuple[int, int] | None) -> None:
        """顔位置に基づいてサーボを更新.

        Args:
            face_center: (x, y) 顔の中心座標、またはNone
        """
        if face_center is None:
            self._handle_face_lost()
            return

        self.tracking = True
        self.lost_count = 0

        face_x, face_y = face_center

        # 画面中心からの誤差を計算
        error_x = self.center_x - face_x  # 顔が左にあれば正
        error_y = face_y - self.center_y  # 顔が上にあれば正

        # デッドゾーン内なら動かさない
        if abs(error_x) < config.DEADZONE_X:
            error_x = 0
        if abs(error_y) < config.DEADZONE_Y:
            error_y = 0

        # PID制御で調整量を計算
        delta_pan = self.pid_pan.compute(error_x)
        delta_tilt = self.pid_tilt.compute(error_y)

        # 現在位置からの相対移動
        pan, tilt = self.servo.get_position()
        target_pan = pan + delta_pan
        target_tilt = tilt + delta_tilt

        # スムージング適用
        self.smooth_pan = self._smooth(self.smooth_pan, target_pan)
        self.smooth_tilt = self._smooth(self.smooth_tilt, target_tilt)

        # サーボ更新
        self.servo.set_position(self.smooth_pan, self.smooth_tilt)

    def _smooth(self, current: float, target: float) -> float:
        """指数移動平均によるスムージング."""
        alpha = config.SMOOTHING_FACTOR
        return current + alpha * (target - current)

    def _handle_face_lost(self) -> None:
        """顔を見失ったときの処理."""
        self.lost_count += 1

        if self.lost_count > self.lost_threshold and self.tracking:
            # 一定時間見失ったら中央に戻る
            self.tracking = False
            self.pid_pan.reset()
            self.pid_tilt.reset()
            self.servo.center()
            self.smooth_pan = config.SERVO_PAN_CENTER
            self.smooth_tilt = config.SERVO_TILT_CENTER
            logger.info("顔をロスト - 中央に復帰")

    def is_tracking(self) -> bool:
        """追跡中かどうか."""
        return self.tracking

    def get_status(self) -> TrackerStatus:
        """現在のステータスを取得."""
        pan, tilt = self.servo.get_position()
        return TrackerStatus(
            tracking=self.tracking,
            pan=pan,
            tilt=tilt,
            lost_count=self.lost_count,
        )
