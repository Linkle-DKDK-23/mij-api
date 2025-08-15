
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

class CreatorStatus:
    PENDING = 1
    VERIFIED = 2
    REJECTED = 3
    SUSPENDED = 4

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