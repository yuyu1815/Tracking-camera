#!/usr/bin/env python3
"""Jetson Nano 顔追尾カメラシステム - メインエントリーポイント."""

from __future__ import annotations

import argparse
import time
from typing import TYPE_CHECKING

import config
import cv2
import numpy as np

from src.camera import Camera
from src.face_detector import FaceDetector, FaceRect
from src.logger import setup_logger
from src.servo_controller import ServoController
from src.tracker import FaceTracker

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = setup_logger()


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース."""
    parser = argparse.ArgumentParser(description="Jetson Nano Face Tracking System")
    parser.add_argument("--no-display", action="store_true", help="映像表示なしで実行")
    parser.add_argument(
        "--usb",
        action="store_true",
        help="USBカメラを使用 (デフォルト: CSIカメラ)",
    )
    return parser.parse_args()


def draw_overlay(
    frame: NDArray[np.uint8],
    tracker: FaceTracker,
    face: FaceRect | None,  # noqa: ARG001
) -> NDArray[np.uint8]:
    """画面にオーバーレイを描画."""
    status = tracker.get_status()

    # 中心線
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (100, 100, 100), 1)
    cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (100, 100, 100), 1)

    # ステータス表示
    if status.tracking:
        color = (0, 255, 0)
        text = f"TRACKING | Pan:{status.pan:.0f} Tilt:{status.tilt:.0f}"
    else:
        color = (0, 0, 255)
        text = "SEARCHING..."

    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return frame


def main() -> None:
    """メイン関数."""
    args = parse_args()

    logger.info("=" * 50)
    logger.info("  Jetson Nano 顔追尾カメラシステム")
    logger.info("=" * 50)

    use_csi = not args.usb
    logger.info(f"カメラモード: {'CSI' if use_csi else 'USB'}")
    logger.info("終了: 'q'キーまたはCtrl+C")

    try:
        with (
            Camera(use_csi=use_csi) as camera,
            ServoController() as servo,
        ):
            detector = FaceDetector()
            tracker = FaceTracker(
                servo,
                config.CAMERA_WIDTH,
                config.CAMERA_HEIGHT,
            )

            # サーボを中央に初期化
            servo.center()
            time.sleep(0.5)

            logger.info("追尾開始...")
            frame_count = 0
            start_time = time.time()

            while True:
                ret, frame = camera.read()
                if not ret or frame is None:
                    logger.error("フレーム取得失敗")
                    break

                # 顔検出
                face = detector.detect_largest(frame)

                # 追尾更新
                if face is not None:
                    face_center = detector.get_face_center(face)
                    tracker.update(face_center)
                    detector.draw_face(frame, face)
                else:
                    tracker.update(None)

                # FPS計算
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    logger.info(f"FPS: {fps:.1f}")

                # 映像表示
                if not args.no_display:
                    frame = draw_overlay(frame, tracker, face)
                    cv2.imshow("Face Tracking", frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    if key == ord("c"):
                        # 'c'キーで中央に戻す
                        servo.center()

    except KeyboardInterrupt:
        logger.info("\n中断されました")
    finally:
        cv2.destroyAllWindows()
        logger.info("終了")


if __name__ == "__main__":
    main()
