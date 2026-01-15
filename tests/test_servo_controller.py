"""ServoControllerのテスト."""

from __future__ import annotations

import config
import pytest

from src.servo_controller import ServoController


class TestServoController:
    """ServoControllerのテスト（シミュレーションモード）."""

    @pytest.fixture
    def servo(self) -> ServoController:
        """テスト用サーボコントローラー."""
        controller = ServoController()
        controller.setup()
        return controller

    def test_init_default_pins(self) -> None:
        """デフォルトピンで初期化されること."""
        servo = ServoController()
        assert servo.pan_pin == config.SERVO_PAN_PIN
        assert servo.tilt_pin == config.SERVO_TILT_PIN

    def test_init_custom_pins(self) -> None:
        """カスタムピンで初期化できること."""
        servo = ServoController(pan_pin=10, tilt_pin=11)
        assert servo.pan_pin == 10
        assert servo.tilt_pin == 11

    def test_initial_angles(self, servo: ServoController) -> None:
        """初期角度が中央であること."""
        assert servo.pan_angle == config.SERVO_PAN_CENTER
        assert servo.tilt_angle == config.SERVO_TILT_CENTER

    def test_set_pan(self, servo: ServoController) -> None:
        """パン角度が設定できること."""
        servo.set_pan(45)
        assert servo.pan_angle == 45

    def test_set_tilt(self, servo: ServoController) -> None:
        """チルト角度が設定できること."""
        servo.set_tilt(60)
        assert servo.tilt_angle == 60

    def test_pan_clamp_min(self, servo: ServoController) -> None:
        """パン角度が最小値でクランプされること."""
        servo.set_pan(-10)
        assert servo.pan_angle == config.SERVO_PAN_MIN

    def test_pan_clamp_max(self, servo: ServoController) -> None:
        """パン角度が最大値でクランプされること."""
        servo.set_pan(200)
        assert servo.pan_angle == config.SERVO_PAN_MAX

    def test_tilt_clamp_min(self, servo: ServoController) -> None:
        """チルト角度が最小値でクランプされること."""
        servo.set_tilt(0)
        assert servo.tilt_angle == config.SERVO_TILT_MIN

    def test_tilt_clamp_max(self, servo: ServoController) -> None:
        """チルト角度が最大値でクランプされること."""
        servo.set_tilt(180)
        assert servo.tilt_angle == config.SERVO_TILT_MAX

    def test_set_position(self, servo: ServoController) -> None:
        """パンとチルトを同時に設定できること."""
        servo.set_position(45, 60)
        assert servo.pan_angle == 45
        assert servo.tilt_angle == 60

    def test_center(self, servo: ServoController) -> None:
        """中央に戻せること."""
        servo.set_position(45, 60)
        servo.center()
        assert servo.pan_angle == config.SERVO_PAN_CENTER
        assert servo.tilt_angle == config.SERVO_TILT_CENTER

    def test_get_position(self, servo: ServoController) -> None:
        """現在位置を取得できること."""
        servo.set_position(45, 60)
        pan, tilt = servo.get_position()
        assert pan == 45
        assert tilt == 60

    def test_angle_to_duty(self, servo: ServoController) -> None:
        """角度がデューティ比に正しく変換されること."""
        assert servo._angle_to_duty(0) == 2.5
        assert servo._angle_to_duty(90) == pytest.approx(7.5)
        assert servo._angle_to_duty(180) == 12.5

    def test_context_manager(self) -> None:
        """コンテキストマネージャーとして使えること."""
        with ServoController() as servo:
            assert servo.initialized is True
