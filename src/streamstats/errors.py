from __future__ import annotations


class StreamStatsError(Exception):
    """Базовое исключение пакета."""

class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат входных данных."""

class InvalidEventError(StreamStatsError):
    """Неверное событие: отсутствует/пустое/неверного типа поле."""

    def __init__(self, message: str, *, file: str | None = None,
                 line: int | None = None, field: str | None = None) -> None:
        self.file = file
        self.line = line
        self.field = field
        parts = [message]
        if file is not None:
            parts.append(f"file={file}")
        if line is not None:
            parts.append(f"line={line}")
        if field is not None:
            parts.append(f"field={field}")
        super().__init__(" | ".join(parts))

class InvalidTimestampError(InvalidEventError):
    """Неверная временная метка."""

class CliConfigError(StreamStatsError):
    """Ошибка конфигурации CLI."""
