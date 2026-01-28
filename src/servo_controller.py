"""サーボモーター制御モジュール - Jetson Nano GPIOを使用したPWM制御."""

from __future__ import annotations

from typing import Any

import config

from src.logger import get_logger

logger = get_logger(__name__)

# Jetson.GPIOはJetson上でのみ利用可能
try:
    import Jetson.GPIO as GPIO

    JETSON_AVAILABLE = True
except ImportError:
    GPIO: Any = None  # type: ignore[no-redef]
    JETSON_AVAILABLE = False
    logger.warning("Jetson.GPIOが利用できません（シミュレーションモード）")


class ServoController:
    """サーボモーター制御クラス."""

    def __init__(self, pan_pin: int | None = None, tilt_pin: int | None = None) -> None:
        """サーボコントローラーを初期化.

        Args:
            pan_pin: パン用サーボのGPIOピン
            tilt_pin: チルト用サーボのGPIOピン
        """
        self.pan_pin = pan_pin or config.SERVO_PAN_PIN
        self.tilt_pin = tilt_pin or config.SERVO_TILT_PIN

        # 現在の角度
        self.pan_angle: float = config.SERVO_PAN_CENTER
        self.tilt_angle: float = config.SERVO_TILT_CENTER

        self.pwm_pan: Any = None
        self.pwm_tilt: Any = None
        self.initialized = False

    def setup(self) -> ServoController:
        """GPIOをセットアップ."""
        if not JETSON_AVAILABLE:
            logger.info("シミュレーションモード: GPIOセットアップをスキップ")
            self.initialized = True
            return self

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pan_pin, GPIO.OUT)
        GPIO.setup(self.tilt_pin, GPIO.OUT)

        # PWM開始
        self.pwm_pan = GPIO.PWM(self.pan_pin, config.PWM_FREQUENCY)
        self.pwm_tilt = GPIO.PWM(self.tilt_pin, config.PWM_FREQUENCY)

        self.pwm_pan.start(self._angle_to_duty(self.pan_angle))
        self.pwm_tilt.start(self._angle_to_duty(self.tilt_angle))

        self.initialized = True
        logger.info(f"サーボ初期化完了: Pan={self.pan_angle}°, Tilt={self.tilt_angle}°")
        return self
    
    def warn_if_simulated(self) -> None:
        """シミュレーションモードの場合に警告を表示."""
        if not JETSON_AVAILABLE:
            print("\n" + "!" * 50)
            print("【警告】シミュレーションモードで実行中")
            print("Jetson.GPIOが検出されませんでした。")
            print("実際のモーターは動作しません。ログ出力のみ行われます。")
            print("!" * 50 + "\n")

    def _angle_to_duty(self, angle: float) -> float:
        """角度をデューティ比に変換.

        SG90サーボ: 0° = 2.5%, 180° = 12.5%
        """
        return 2.5 + (angle / 180.0) * 10.0

    def _clamp_pan(self, angle: float) -> float:
        """パン角度を制限範囲内に収める."""
        return max(config.SERVO_PAN_MIN, min(config.SERVO_PAN_MAX, angle))

    def _clamp_tilt(self, angle: float) -> float:
        """チルト角度を制限範囲内に収める."""
        return max(config.SERVO_TILT_MIN, min(config.SERVO_TILT_MAX, angle))

    def set_pan(self, angle: float) -> None:
        """パン角度を設定.

        Args:
            angle: 目標角度 (0-180)
        """
        self.pan_angle = self._clamp_pan(angle)

        if JETSON_AVAILABLE and self.pwm_pan:
            self.pwm_pan.ChangeDutyCycle(self._angle_to_duty(self.pan_angle))
        else:
            logger.debug(f"[SIM] Pan: {self.pan_angle}°")
            # 最初の1回だけ警告を出すなどの処理を入れても良いが、
            # 現状はログ出力のみとする

    def set_tilt(self, angle: float) -> None:
        """チルト角度を設定.

        Args:
            angle: 目標角度 (30-150)
        """
        self.tilt_angle = self._clamp_tilt(angle)

        if JETSON_AVAILABLE and self.pwm_tilt:
            self.pwm_tilt.ChangeDutyCycle(self._angle_to_duty(self.tilt_angle))
        else:
            logger.debug(f"[SIM] Tilt: {self.tilt_angle}°")

    def set_position(self, pan: float, tilt: float) -> None:
        """パンとチルトを同時に設定."""
        self.set_pan(pan)
        self.set_tilt(tilt)

    def center(self) -> None:
        """サーボを中央位置に戻す."""
        self.set_position(config.SERVO_PAN_CENTER, config.SERVO_TILT_CENTER)

    def get_position(self) -> tuple[float, float]:
        """現在の位置を取得."""
        return self.pan_angle, self.tilt_angle

    def cleanup(self) -> None:
        """GPIOをクリーンアップ."""
        if JETSON_AVAILABLE:
            if self.pwm_pan:
                self.pwm_pan.stop()
            if self.pwm_tilt:
                self.pwm_tilt.stop()
            GPIO.cleanup()
        logger.info("サーボ停止")

    def __enter__(self) -> ServoController:
        return self.setup()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.cleanup()


if __name__ == "__main__":
    import time

    logger.info("サーボテスト")
    with ServoController() as servo:
        # 中央
        logger.info("中央位置")
        servo.center()
        time.sleep(1)

        # パンテスト
        logger.info("パン: 左")
        servo.set_pan(45)
        time.sleep(0.5)
        logger.info("パン: 右")
        servo.set_pan(135)
        time.sleep(0.5)
        servo.set_pan(90)

        # チルトテスト
        logger.info("チルト: 上")
        servo.set_tilt(60)
        time.sleep(0.5)
        logger.info("チルト: 下")
        servo.set_tilt(120)
        time.sleep(0.5)

        # 中央に戻す
        servo.center()
        logger.info("テスト完了")
