"""Enums shared across models."""
import enum


class UserRole(str, enum.Enum):
    client = "client"
    artisan = "artisan"


class SpecialtyEnum(str, enum.Enum):
    zlayji = "zlayji"
    sebbagh = "sebbagh"
    gebbas = "gebbas"
    plombier = "plombier"
    electricien = "electricien"


class ComplexityEnum(str, enum.Enum):
    simple = "simple"
    moyenne = "moyenne"
    complexe = "complexe"


class JobStatusEnum(str, enum.Enum):
    pending = "pending"
    matching = "matching"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"
    cancelled = "cancelled"


class MatchingResponseEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    refused = "refused"
    no_response = "no_response"


class GuaranteeStatusEnum(str, enum.Enum):
    open = "open"
    claimed = "claimed"
    resolved = "resolved"
    expired = "expired"


class PaymentStatusEnum(str, enum.Enum):
    held = "held"
    released = "released"
    refunded = "refunded"
