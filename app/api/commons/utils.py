import random
import string

def generate_code(length: int = 5) -> str:
    """
    ランダムなコードを生成

    Args:
        length (int): コードの長さ

    Returns:
        str: ランダムなコード
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def get_video_duration(duration_sec: float) -> str:
    """
    動画の再生時間をmm:ss形式に変換

    Args:
        duration_sec (float): 動画の再生時間（秒）

    Returns:
        str: mm:ss形式の動画の再生時間
    """
    # 四捨五入して整数秒に変換
    rounded_sec = round(duration_sec)
    minutes = rounded_sec // 60
    seconds = rounded_sec % 60
    return f"{minutes:02d}:{seconds:02d}"