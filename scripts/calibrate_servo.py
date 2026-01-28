#!/usr/bin/env python3
"""サーボキャリブレーションスクリプト - サーボの動作範囲を確認・調整."""

from __future__ import annotations

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logger
from src.servo_controller import ServoController

logger = setup_logger()


def main() -> None:
    """メイン関数."""
    logger.info("=" * 50)
    logger.info("  サーボキャリブレーション")
    logger.info("=" * 50)
    logger.info("コマンド:")
    logger.info("  p <角度>  - パン角度を設定 (0-180)")
    logger.info("  t <角度>  - チルト角度を設定 (30-150)")
    logger.info("  c         - 中央に戻す")
    logger.info("  q         - 終了")

    with ServoController() as servo:
        servo.warn_if_simulated()
        servo.center()
        logger.info("初期位置: Pan=90°, Tilt=90°")

        while True:
            try:
                cmd = input("> ").strip().lower()

                if cmd == "q":
                    break
                elif cmd == "c":
                    servo.center()
                    logger.info("中央に移動")
                elif cmd.startswith("p "):
                    try:
                        angle = float(cmd[2:])
                        servo.set_pan(angle)
                        logger.info(f"Pan: {servo.pan_angle}°")
                    except ValueError:
                        logger.warning("無効な角度")
                elif cmd.startswith("t "):
                    try:
                        angle = float(cmd[2:])
                        servo.set_tilt(angle)
                        logger.info(f"Tilt: {servo.tilt_angle}°")
                    except ValueError:
                        logger.warning("無効な角度")
                else:
                    pan, tilt = servo.get_position()
                    logger.info(f"現在位置: Pan={pan}°, Tilt={tilt}°")

            except KeyboardInterrupt:
                break

    logger.info("終了")


if __name__ == "__main__":
    main()
