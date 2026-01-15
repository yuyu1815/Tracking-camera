"""PIDController と FaceTracker のテスト."""

from __future__ import annotations

from unittest.mock import MagicMock

import config
import pytest

from src.tracker import FaceTracker, PIDController, TrackerStatus


class TestPIDController:
    """PIDControllerのテスト."""

    def test_init_default_values(self) -> None:
        """デフォルト値で初期化できること."""
        pid = PIDController()
        assert pid.kp == config.PID_KP
        assert pid.ki == config.PID_KI
        assert pid.kd == config.PID_KD

    def test_init_custom_values(self) -> None:
        """カスタム値で初期化できること."""
        pid = PIDController(kp=1.0, ki=0.5, kd=0.2)
        assert pid.kp == 1.0
        assert pid.ki == 0.5
        assert pid.kd == 0.2

    def test_compute_proportional(self) -> None:
        """比例制御が正しく計算されること."""
        pid = PIDController(kp=1.0, ki=0.0, kd=0.0)
        output = pid.compute(10.0)
        assert output == 10.0  # kp * error = 1.0 * 10.0

    def test_compute_integral(self) -> None:
        """積分制御が正しく計算されること."""
        pid = PIDController(kp=0.0, ki=1.0, kd=0.0)
        pid.compute(5.0)  # integral = 5.0
        output = pid.compute(5.0)  # integral = 10.0
        assert output == 10.0  # ki * integral = 1.0 * 10.0

    def test_compute_derivative(self) -> None:
        """微分制御が正しく計算されること."""
        pid = PIDController(kp=0.0, ki=0.0, kd=1.0)
        pid.compute(0.0)  # prev_error = 0
        output = pid.compute(10.0)  # derivative = 10 - 0 = 10
        assert output == 10.0  # kd * derivative = 1.0 * 10.0

    def test_reset(self) -> None:
        """リセットで状態がクリアされること."""
        pid = PIDController(kp=1.0, ki=1.0, kd=1.0)
        pid.compute(10.0)
        pid.compute(20.0)
        pid.reset()
        assert pid.prev_error == 0
        assert pid.integral == 0


class TestFaceTracker:
    """FaceTrackerのテスト."""

    @pytest.fixture
    def mock_servo(self) -> MagicMock:
        """モックサーボコントローラー."""
        servo = MagicMock()
        servo.get_position.return_value = (90.0, 90.0)
        return servo

    @pytest.fixture
    def tracker(self, mock_servo: MagicMock) -> FaceTracker:
        """テスト用トラッカー."""
        return FaceTracker(mock_servo, frame_width=640, frame_height=480)

    def test_init(self, tracker: FaceTracker) -> None:
        """正しく初期化されること."""
        assert tracker.frame_width == 640
        assert tracker.frame_height == 480
        assert tracker.center_x == 320
        assert tracker.center_y == 240
        assert not tracker.tracking

    def test_update_with_face_at_center(self, tracker: FaceTracker) -> None:
        """顔が中央にあるとき、サーボがほぼ動かないこと."""
        # 中央付近 (デッドゾーン内)
        tracker.update((320, 240))
        assert tracker.tracking is True
        assert tracker.lost_count == 0

    def test_update_with_face_off_center(self, tracker: FaceTracker, mock_servo: MagicMock) -> None:
        """顔が中央からずれているとき、サーボが動くこと."""
        tracker.update((100, 100))
        mock_servo.set_position.assert_called()
        assert tracker.tracking is True

    def test_update_with_no_face(self, tracker: FaceTracker) -> None:
        """顔が検出されないとき、lost_countが増えること."""
        tracker.update(None)
        assert tracker.lost_count == 1
        tracker.update(None)
        assert tracker.lost_count == 2

    def test_face_lost_returns_to_center(self, tracker: FaceTracker, mock_servo: MagicMock) -> None:
        """一定時間顔を見失ったら中央に戻ること."""
        tracker.tracking = True
        tracker.lost_threshold = 3  # テスト用に小さく

        for _ in range(4):
            tracker.update(None)

        mock_servo.center.assert_called()
        assert not tracker.tracking

    def test_is_tracking(self, tracker: FaceTracker) -> None:
        """追跡状態の取得."""
        assert tracker.is_tracking() is False
        tracker.update((320, 240))
        assert tracker.is_tracking() is True

    def test_get_status(self, tracker: FaceTracker) -> None:
        """ステータス取得."""
        status = tracker.get_status()
        assert isinstance(status, TrackerStatus)
        assert status.tracking is False
        assert status.pan == 90.0
        assert status.tilt == 90.0
        assert status.lost_count == 0
