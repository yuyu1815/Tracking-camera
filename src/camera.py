"""カメラ制御モジュール - CSIカメラからのフレーム取得を担当."""

from __future__ import annotations

from typing import TYPE_CHECKING

import config
import cv2
import numpy as np

from src.logger import get_logger

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = get_logger(__name__)


class Camera:
    """CSIカメラからフレームを取得するクラス."""

    def __init__(self, use_csi: bool = True) -> None:
        """カメラを初期化.

        Args:
            use_csi: CSIカメラを使用する場合True、USBカメラはFalse
        """
        self.use_csi = use_csi
        self.cap: cv2.VideoCapture | None = None
        self.width = config.CAMERA_WIDTH
        self.height = config.CAMERA_HEIGHT

    def start(self) -> Camera:
        """カメラを起動."""
        if self.use_csi:
            # CSIカメラ (GStreamerパイプライン使用)
            logger.info("CSIカメラを初期化中 (GStreamer)...")
            self.cap = cv2.VideoCapture(config.GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
        else:
            # USBカメラ
            logger.info("USBカメラを初期化中...")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

        if not self.cap.isOpened():
            msg = "カメラを開けませんでした"
            logger.error(msg)
            raise RuntimeError(msg)

        logger.info(f"カメラ起動完了: {self.width}x{self.height}")
        return self

    def read(self) -> tuple[bool, NDArray[np.uint8] | None]:
        """フレームを取得.

        Returns:
            tuple: (成功フラグ, フレーム画像)
        """
        if self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        return ret, frame if ret else None

    def get_center(self) -> tuple[int, int]:
        """画面中心座標を取得."""
        return self.width // 2, self.height // 2

    def stop(self) -> None:
        """カメラを停止."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("カメラ停止")

    def __enter__(self) -> Camera:
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.stop()


if __name__ == "__main__":
    # テスト実行
    with Camera(use_csi=False) as cam:  # 開発環境ではUSBカメラ
        logger.info("カメラテスト - 'q'で終了")
        while True:
            ret, frame = cam.read()
            if not ret or frame is None:
                break
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()
