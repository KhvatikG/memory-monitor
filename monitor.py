import time
import logging
import json

import requests

import psutil

logging.basicConfig(level=logging.DEBUG)

# Эндпоинт для отправки alarm:
ENDPOINT_URL: str = ""

# Критическое значение памяти при котором отправляется alarm
CRITICAL_VALUE_IN_PERCENT: int = 70

# Частота проверки памяти в секундах
SLIP_TIME = 3


class MemoryChecker:
    """
    Класс для мониторинга использования памяти и отправки уведомлений при превышении заданного порога.
    """
    def __init__(
            self,
            endpoint: str,
            critical_memory_value: int,
            memory_test_freq: int,

    ):
        """

        :param endpoint: Конечная точка API для отправки показателя.
        :param critical_memory_value: верхняя граница использования памяти
        :param memory_test_freq: Промежуток между проверкой памяти в секундах.
        """
        self.endpoint = endpoint
        self.critical_memory_value = critical_memory_value
        self.memory_test_freq = memory_test_freq

    def send_memory_alarm(self, mem_usage_percent: int) -> None:
        """
        Отправляет POST запрос на endpoint со значением mem_usage_percent.

        :param mem_usage_percent: процентный показатель используемой памяти
        """
        data = {
            "message": "memory_limit_alarm",
            "mem_usage_percent": mem_usage_percent
        }

        response = requests.post(url=self.endpoint, json=data)

        if response.status_code != 200:
            logging.critical(f'НЕУДАЛОСЬ ОТПРАВИТЬ! status = {response.status_code}')
        else:
            logging.info(f'Сообщение о превышении лимита памяти отправлено')

    def check_memory(self) -> None:
        """
        Если процентный показатель используемой памяти(mem_usage_percent) выше значения alarm,
        отправляет POST запрос на endpoint со значением mem_usage_percent с помощью send_memory_alarm.
        """
        mem_stat = psutil.virtual_memory()
        memory_usage_percent = mem_stat[2]  # процентный показатель используемой памяти

        if memory_usage_percent > self.critical_memory_value:
            logging.warning(f'Лимит памяти превышен отправляю предупреждение на {self.endpoint}')
            self.send_memory_alarm(memory_usage_percent)

    def start_memory_checking(self) -> None:
        """
        Проверяет память каждые self.memory_test_freq секунд с помощью self.check_memory
        и отправляет alarm POST запросом с помощью self.send_memory_alarm
        """
        if not self.endpoint:
           logging.error('Не указан endpoint для отправки alarm.')
           return
        try:
            while True:
                self.check_memory()
                time.sleep(self.memory_test_freq)

        except KeyboardInterrupt:
            logging.info('Завершено.')
        except Exception as e:
            logging.error(f'Произошла ошибка {e}')


memory_checker = MemoryChecker(
    endpoint=ENDPOINT_URL,
    critical_memory_value=CRITICAL_VALUE_IN_PERCENT,
    memory_test_freq=SLIP_TIME

)


if __name__ == '__main__':
    logging.info('Запущен.')
    memory_checker.start_memory_checking()
