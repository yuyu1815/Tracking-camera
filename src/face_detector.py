"""顔検出モジュール - OpenCV Haar Cascadeを使用した顔検出."""

from __future__ import annotations

from typing import TYPE_CHECKING

import config
import cv2
import numpy as np

from src.logger import get_logger

if TYPE_CHECKING:
    from numpy.typing import NDArray

# 顔矩形の型: (x, y, width, height)
FaceRect = tuple[int, int, int, int]

logger = get_logger(__name__)


class FaceDetector:
    """Haar Cascadeベースの顔検出クラス."""

    def __init__(self) -> None:
        """顔検出器を初期化."""
        self.face_cascade = cv2.CascadeClassifier(config.FACE_CASCADE_PATH)

        # カスケードファイルが読み込めない場合はOpenCVのデフォルトを試す
        if self.face_cascade.empty():
            logger.warning(
                "指定されたカスケードファイルが見つかりません: %s. "
                "デフォルトのカスケードを試行します.",
                config.FACE_CASCADE_PATH,
            )
            default_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(default_path)

        if self.face_cascade.empty():
            msg = "顔検出カスケードファイルを読み込めませんでした"
            logger.critical(msg)
            raise RuntimeError(msg)

        logger.info("顔検出器を初期化しました")

    def detect(self, frame: NDArray[np.uint8]) -> list[FaceRect]:
        """フレームから顔を検出.

        Args:
            frame: BGR画像フレーム

        Returns:
            list: 検出された顔の矩形 [(x, y, w, h), ...]
        """
        # グレースケールに変換
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 顔検出
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=config.DETECTION_SCALE_FACTOR,
            minNeighbors=config.DETECTION_MIN_NEIGHBORS,
            minSize=config.DETECTION_MIN_SIZE,
        )

        return [tuple(f) for f in faces]  # type: ignore[misc]

    def detect_largest(self, frame: NDArray[np.uint8]) -> FaceRect | None:
        """最も大きい顔を検出（追尾対象）.

        Args:
            frame: BGR画像フレーム

        Returns:
            tuple: (x, y, w, h) または None
        """
        faces = self.detect(frame)

        if len(faces) == 0:
            return None

        # 面積が最大の顔を選択
        return max(faces, key=lambda f: f[2] * f[3])

    def get_face_center(self, face_rect: FaceRect) -> tuple[int, int]:
        """顔の中心座標を計算.

        Args:
            face_rect: (x, y, w, h) 顔の矩形

        Returns:
            tuple: (center_x, center_y)
        """
        x, y, w, h = face_rect
        return x + w // 2, y + h // 2

    def draw_face(
        self,
        frame: NDArray[np.uint8],
        face_rect: FaceRect,
        color: tuple[int, int, int] = (0, 255, 0),
    ) -> None:
        """顔の矩形を描画.

        Args:
            frame: 描画対象のフレーム
            face_rect: (x, y, w, h) 顔の矩形
            color: BGR色
        """
        x, y, w, h = face_rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # 中心にマーカー
        cx, cy = self.get_face_center(face_rect)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)


if __name__ == "__main__":
    from src.camera import Camera

    detector = FaceDetector()

    with Camera(use_csi=False) as cam:
        logger.info("顔検出テスト - 'q'で終了")
        while True:
            ret, frame = cam.read()
            if not ret or frame is None:
                break

            # 顔検出
            face = detector.detect_largest(frame)
            if face is not None:
                detector.draw_face(frame, face)
                cx, cy = detector.get_face_center(face)
                cv2.putText(
                    frame,
                    f"Face: ({cx}, {cy})",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

            cv2.imshow("Face Detection Test", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()
