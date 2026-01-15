"""ロギング設定モジュール."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "jetson_face_tracker") -> logging.Logger:
    """ロガーをセットアップして取得.

    Args:
        name: ロガー名

    Returns:
        logging.Logger: 設定済みロガー
    """
    logger = logging.getLogger(name)

    # 既にハンドラーが設定されている場合は何もしない
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # 標準出力へのハンドラー
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    # ログフォーマット
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # ファイルへのハンドラー
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """モジュール用ロガーを取得.

    Args:
        name: モジュール名 (__name__)

    Returns:
        logging.Logger: 子ロガー
    """
    # ルートロガーの設定を確認/実行
    setup_logger()
    return logging.getLogger(f"jetson_face_tracker.{name}")
