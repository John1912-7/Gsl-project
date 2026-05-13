from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    STANDARD = "Standard"
    VIP = "VIP"
    BACKSTAGE = "Backstage"


class Status(Enum):
    VALID = "Valid"
    USED = "Used"
    EXPIRED = "Expired"


@dataclass
class Ticket:
    code: str
    category: Category = Category.STANDARD
    status: Status = Status.VALID
