
# アカウント種別
class AccountType:
    # 一般ユーザー
    GENERAL_USER = 1
    # クリエイター
    CREATOR = 2
    # 管理者
    ADMIN = 3

# アカウントステータス
class AccountStatus:
    # 有効
    ACTIVE = 1
    # 無効
    INACTIVE = 2
    # 停止
    SUSPENDED = 3
    # 削除
    DELETED = 4

# クリエイターステータス
class CreatorStatus:
    # 入力済み
    ENTERED = 1
    # 申請中
    APPLICATED = 2
    # 本人確認済み
    VERIFIED = 3
    # 拒否
    REJECTED = 4
    # 停止
    SUSPENDED = 5

class VerificationStatus:
    # 未承認
    PENDING = 0
    # 承認
    APPROVED = 1
    # 拒否
    REJECTED = 2

class IdentityStatus:
    # 未承認
    PENDING = 0
    # 承認
    APPROVED = 1
    # 拒否
    REJECTED = 2

class IdentityKind:
    # 本人確認書類（正面）
    FRONT = 1
    # 本人確認書類（背面）
    BACK = 2
    # 本人確認書類（本人写真）
    SELFIE = 3

class PostStatus:
    # 未承認
    PENDING = 1
    REJECTED = 2
    # 非公開
    UNPUBLISHED = 3
    # 削除
    DELETED = 4
    # 公開
    APPROVED = 5

class PostVisibility:
    # 単品
    SINGLE = 1
    # プラン
    PLAN = 2
    # 両方
    BOTH = 3

class PlanStatus:
    # 単品
    SINGLE = 1
    # プラン
    PLAN = 2

class PriceType:
    # 単品
    SINGLE = 1
    # プラン
    PLAN = 2

# メディアアセットのkind
class MediaAssetKind:
    # OGP画像
    OGP = 1
    # サムネイル画像
    THUMBNAIL = 2
    # 画像（複数）
    IMAGES = 3
    # メインビデオ
    MAIN_VIDEO = 4
    # サンプルビデオ
    SAMPLE_VIDEO = 5


class RenditionKind:
    # プレビュービデオ
    PREVIEW_MP4 = 1
    # HLS_ABR4
    HLS_ABR4 = 2

class RenditionBackend:
    # MediaConvert
    MEDIACONVERT = 1
    # Fargate FFmpeg
    FARGATE_FFMPEG = 2

class RenditionJobStatus:
    # 未実行
    PENDING = 1
    # 実行中
    SUBMITTED = 2
    # 進行中
    PROGRESSING = 3
    # 完了
    COMPLETE = 4
    # エラー
    ERROR = 9

class MediaRenditionJobKind:
    # プレビュービデオ
    PREVIEW_MP4 = 1
    # HLS_ABR4
    HLS_ABR4 = 2

class MediaRenditionJobBackend:
    # MediaConvert
    MEDIACONVERT = 1
    # Fargate FFmpeg
    FARGATE_FFMPEG = 2

class MediaRenditionJobStatus:
    # 未実行
    PENDING = 1
    # 実行中
    SUBMITTED = 2
    # 進行中
    PROGRESSING = 3
    # 完了
    COMPLETE = 4
    # エラー
    FAILED = 5

class MediaRenditionKind:
    HLS_MASTER = 10
    HLS_VARIANT_360P  = 11
    HLS_VARIANT_480P  = 12
    HLS_VARIANT_720P  = 13
    HLS_VARIANT_1080P = 14