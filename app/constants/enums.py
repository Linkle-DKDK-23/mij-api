
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