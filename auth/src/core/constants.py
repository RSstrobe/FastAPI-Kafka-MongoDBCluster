from enum import Enum


class UserRoleEnum(str, Enum):
    DefaultUser = "DefaultUser"
    Admin = "Admin"
