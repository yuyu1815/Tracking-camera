#!/usr/bin/env python3
"""カメラテストスクリプト."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.camera import Camera
from src.logger import setup_logger

logger = setup_logger()


def main() -> None:
    """メイン関数."""
    logger.info("カメラテスト - 'q'で終了")

    # CSIカメラで試す
    use_csi = True
    logger.info("CSIカメラモードで起動中...")

    try:
        with Camera(use_csi=use_csi) as cam:
            while True:
                ret, frame = cam.read()
                if not ret or frame is None:
                    logger.error("フレーム取得失敗")
                    break

                # 解像度表示
                h, w = frame.shape[:2]
                cv2.putText(
                    frame,
                    f"{w}x{h}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

                cv2.imshow("Camera Test", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except RuntimeError as e:
        logger.warning(f"CSIカメラでエラー: {e}")
        logger.info("USBカメラを試します...")

        with Camera(use_csi=False) as cam:
            while True:
                ret, frame = cam.read()
                if not ret or frame is None:
                    break
                cv2.imshow("Camera Test (USB)", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    cv2.destroyAllWindows()
    logger.info("終了")


if __name__ == "__main__":
    main()
