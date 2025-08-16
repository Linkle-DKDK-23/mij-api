
# アカウント種別
class AccountType:
    GENERAL_USER = 1
    CREATOR = 2
    ADMIN = 3

# アカウントステータス
class AccountStatus:
    ACTIVE = 1
    INACTIVE = 2
    SUSPENDED = 3
    DELETED = 4

# クリエイターステータス
class CreatorStatus:
    ENTERED = 1
    APPLICATED = 2
    VERIFIED = 3
    REJECTED = 4
    SUSPENDED = 5

class VerificationStatus:
    PENDING = 0
    APPROVED = 1
    REJECTED = 2

class IdentityStatus:
    PENDING = 0
    APPROVED = 1
    REJECTED = 2

class IdentityKind:
    FRONT = 1
    BACK = 2
    SELFIE = 3

class PostStatus:
    PENDING = 1
    REJECTED = 2
    UNPUBLISHED = 3
    DELETED = 4
    APPROVED = 5