from enum import StrEnum, unique


@unique
class OperationTypeEnum(StrEnum):
    DEPOSIT = "Пополнение"
    WITHDRAW = "Списание"
