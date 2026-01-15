"""設定ファイルのテスト."""

from __future__ import annotations

import config


class TestConfig:
    """config.pyのテスト."""

    def test_camera_settings(self) -> None:
        """カメラ設定が正しいこと."""
        assert config.CAMERA_WIDTH > 0
        assert config.CAMERA_HEIGHT > 0
        assert config.CAMERA_FPS > 0

    def test_servo_pan_settings(self) -> None:
        """パンサーボ設定が正しいこと."""
        assert config.SERVO_PAN_MIN <= config.SERVO_PAN_CENTER <= config.SERVO_PAN_MAX
        assert config.SERVO_PAN_MIN >= 0
        assert config.SERVO_PAN_MAX <= 180

    def test_servo_tilt_settings(self) -> None:
        """チルトサーボ設定が正しいこと."""
        assert config.SERVO_TILT_MIN <= config.SERVO_TILT_CENTER <= config.SERVO_TILT_MAX
        assert config.SERVO_TILT_MIN >= 0
        assert config.SERVO_TILT_MAX <= 180

    def test_pid_settings(self) -> None:
        """PID設定が正しいこと."""
        assert config.PID_KP >= 0
        assert config.PID_KI >= 0
        assert config.PID_KD >= 0

    def test_deadzone_settings(self) -> None:
        """デッドゾーン設定が正しいこと."""
        assert config.DEADZONE_X > 0
        assert config.DEADZONE_Y > 0

    def test_smoothing_factor(self) -> None:
        """スムージング係数が範囲内であること."""
        assert 0.0 <= config.SMOOTHING_FACTOR <= 1.0

    def test_detection_settings(self) -> None:
        """検出設定が正しいこと."""
        assert config.DETECTION_SCALE_FACTOR > 1.0
        assert config.DETECTION_MIN_NEIGHBORS > 0
        assert len(config.DETECTION_MIN_SIZE) == 2
        assert all(s > 0 for s in config.DETECTION_MIN_SIZE)
