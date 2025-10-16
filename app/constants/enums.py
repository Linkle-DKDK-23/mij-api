
# アカウント種別
class AccountType:
    GENERAL_USER = 1 # 一般ユーザー
    CREATOR = 2 # クリエイター
    ADMIN = 3 # 管理者

# アカウントステータス
class AccountStatus:
    ACTIVE = 1 # 有効
    INACTIVE = 2 # 無効
    SUSPENDED = 3 # 停止
    DELETED = 4 # 削除

# クリエイターステータス
class CreatorStatus:
    ENTERED = 1 # 入力済み
    APPLICATED = 2 # 申請中
    VERIFIED = 3 # 本人確認済み
    REJECTED = 4 # 拒否
    SUSPENDED = 5 # 停止

# 本人確認ステータス
class VerificationStatus:
    PENDING = 0 # 未承認
    APPROVED = 1 # 承認
    REJECTED = 2 # 拒否

# 本人確認ステータス
class IdentityStatus:
    PENDING = 0 # 未承認
    APPROVED = 1 # 承認
    REJECTED = 2 # 拒否

# 本人確認書類の種類
class IdentityKind:
    FRONT = 1 # 本人確認書類（正面）
    BACK = 2 # 本人確認書類（背面）
    SELFIE = 3 # 本人確認書類（本人写真）

# 投稿ステータス
class PostStatus:
    PENDING = 1 # 未承認
    REJECTED = 2 # 拒否
    UNPUBLISHED = 3 # 非公開
    DELETED = 4 # 削除
    APPROVED = 5 # 公開

# 投稿の種類
class PostType:
    VIDEO = 1 # ビデオ
    IMAGE = 2 # 画像

# 投稿の公開範囲
class PostVisibility:
    SINGLE = 1 # 単品
    PLAN = 2 # プラン
    BOTH = 3 # 両方

# プランステータス
class PlanStatus:
    SINGLE = 1 # 単品
    PLAN = 2 # プラン

# プランの種類
class PriceType:
    SINGLE = 1 # 単品
    PLAN = 2 # プラン

# メディアアセットのkind
class MediaAssetKind:
    OGP = 1 # OGP画像
    THUMBNAIL = 2 # サムネイル画像
    IMAGES = 3 # 画像（複数）
    MAIN_VIDEO = 4 # メインビデオ
    SAMPLE_VIDEO = 5 # サンプルビデオ
    IMAGE_ORIGINAL = 6 # 画像（オリジナル）
    IMAGE_1080W = 7 # 画像（1080w）
    IMAGE_MOSAIC = 8 # 画像（モザイク）

# レンディションの種類
class RenditionKind:
    PREVIEW_MP4 = 1 # プレビュービデオ
    HLS_ABR4 = 2 # HLS_ABR4

# レンディションのバックエンド
class RenditionBackend:
    MEDIACONVERT = 1 # MediaConvert
    FARGATE_FFMPEG = 2 # Fargate FFmpeg

# レンディションのステータス
class RenditionJobStatus:
    PENDING = 1 # 未実行
    SUBMITTED = 2 # 実行中
    PROGRESSING = 3 # 進行中
    COMPLETE = 4 # 完了
    ERROR = 9 # エラー

# メディアレンディションの種類
class MediaRenditionJobKind:
    PREVIEW_MP4 = 1 # プレビュービデオ
    HLS_ABR4 = 2 # HLS_ABR4

# メディアレンディションのバックエンド
class MediaRenditionJobBackend:
    MEDIACONVERT = 1 # MediaConvert
    FARGATE_FFMPEG = 2 # Fargate FFmpeg

# メディアレンディションのステータス
class MediaRenditionJobStatus:
    PENDING = 1 # 未実行
    SUBMITTED = 2 # 実行中
    PROGRESSING = 3 # 進行中
    COMPLETE = 4 # 完了
    FAILED = 5 # エラー

# メディアレンディションの種類
class MediaRenditionKind:
    HLS_MASTER = 10 # HLS_MASTER
    HLS_VARIANT_360P  = 11 # HLS_VARIANT_360P
    HLS_VARIANT_480P  = 12 # HLS_VARIANT_480P
    HLS_VARIANT_720P  = 13 # HLS_VARIANT_720P
    HLS_VARIANT_1080P = 14 # HLS_VARIANT_1080P
    FFMPEG = 20 # FFMPEG

# 会話の種類
class ConversationType:
    SUPPORT = 1 # サポート会話
    DM = 2 # DM
    GROUP = 3 # グループ
    DELUSION = 4 # 妄想の間

# メディアアセットの向き
class MediaAssetOrientation:
    PORTRAIT = 1 # 縦
    LANDSCAPE = 2 # 横
    SQUARE = 3 # 正方形