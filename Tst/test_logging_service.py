import os
import json
import pytest
from Src.settings_manager import settings_manager
from Src.Core.logging_service import logging_service, emit
from Src.Core import log_levels


LOG_DIR = os.path.join(os.getcwd(), "logs")
SETTINGS_FILE = os.path.join(os.getcwd(), "Docs", "settings.json")


@pytest.fixture
def sm():
    """
    Создаём settings_manager с явным файлом Docs/settings.json.
    Singleton, но для тестов важно вызвать явно.
    """
    sm = settings_manager()
    sm.file_name = SETTINGS_FILE
    return sm


@pytest.fixture
def log_service_real(sm):
    """
    Инстанс logging_service, который пишет реально в ./logs.
    Настройки не грузим через reload — тест управляет ими вручную.
    """
    ls = logging_service(sm)
    ls.mode = 'file'
    ls.log_dir = LOG_DIR
    ls.level = log_levels.DEBUG  # логируем всё
    ls.format = '{date} [{level}] {message} {meta}'
    return ls


def get_latest_log_file():
    """Получаем путь к последнему лог-файлу"""
    if not os.path.exists(LOG_DIR):
        return None
    files = os.listdir(LOG_DIR)
    if not files:
        return None
    return max([os.path.join(LOG_DIR, f) for f in files], key=os.path.getctime)


def read_log_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def test_log_file_creation_and_write(log_service_real):
    # Удаляем старый файл для чистоты теста
    latest_file = get_latest_log_file()
    if latest_file and os.path.exists(latest_file):
        os.remove(latest_file)

    # Логируем разные сообщения
    log_service_real.handle('log', {'level': 'DEBUG', 'message': 'Debug message'})
    log_service_real.handle('log', {'level': 'INFO', 'message': 'Info message'})
    log_service_real.handle('log', {'level': 'ERROR', 'message': 'Error message'})

    # Проверяем, что файл логов появился
    latest_file = get_latest_log_file()
    assert latest_file is not None
    assert os.path.isfile(latest_file)

    # Проверяем, что все сообщения попали в файл
    content = read_log_file(latest_file)
    assert 'Debug message' in content
    assert 'Info message' in content
    assert 'Error message' in content


def test_log_with_meta_real(log_service_real):
    meta_data = {'user': 'tester', 'action': 'test'}
    log_service_real.handle(
        'log',
        {'level': 'INFO', 'message': 'Message with meta', 'meta': meta_data}
    )

    latest_file = get_latest_log_file()
    content = read_log_file(latest_file)

    assert 'Message with meta' in content
    assert json.dumps(meta_data) in content


def test_emit_real(log_service_real):
    # Проверяем работу emit
    emit('INFO', 'Emit test message', {'key': 'value'})

    latest_file = get_latest_log_file()
    content = read_log_file(latest_file)

    assert 'Emit test message' in content
    assert '"key": "value"' in content
