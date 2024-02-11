from dataclasses import dataclass


@dataclass
class role:
    SYSYEM: str = 'system'
    USER: str = 'user'
    ASSISTANT: str = 'assistant'


def userQuestion(message):
    pass