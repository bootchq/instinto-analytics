#!/usr/bin/env python3
"""
Автоматический логин в RetailCRM через Playwright.
Получает x-client-token для GraphQL API.
"""

import os
import json
import time
from playwright.sync_api import sync_playwright


def get_retailcrm_token(login: str, password: str, headless: bool = True) -> str:
    """
    Логинится в RetailCRM и получает x-client-token из запросов.

    Args:
        login: Email для входа
        password: Пароль
        headless: Запускать браузер без GUI

    Returns:
        x-client-token для GraphQL запросов
    """
    token = None

    with sync_playwright() as p:
        # Запускаем браузер
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # Перехватываем запросы для получения токена
        def handle_request(request):
            nonlocal token
            if 'batch' in request.url or 'graphql' in request.url:
                headers = request.headers
                if 'x-client-token' in headers:
                    token = headers['x-client-token']
                    print(f"Получен токен: {token[:20]}...")

        page.on('request', handle_request)

        # Переходим на страницу логина
        print("Открываю страницу логина...")
        page.goto('https://instinto.retailcrm.ru/login', wait_until='networkidle')
        time.sleep(2)

        # Вводим логин
        print("Ввожу логин...")
        login_input = page.locator('input[name="email"], input[name="login"], input[type="email"]').first
        login_input.fill(login)

        # Вводим пароль
        print("Ввожу пароль...")
        password_input = page.locator('input[name="password"], input[type="password"]').first
        password_input.fill(password)

        # Нажимаем кнопку входа
        print("Нажимаю кнопку входа...")
        submit_button = page.locator('button[type="submit"], input[type="submit"], .login-button, .btn-login').first
        submit_button.click()

        # Ждём загрузки
        print("Жду загрузки...")
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Переходим в чаты чтобы получить токен
        print("Перехожу в раздел чатов...")
        page.goto('https://instinto.retailcrm.ru/analytics/communication/chats', wait_until='networkidle')
        time.sleep(5)

        # Если токен ещё не получен, пробуем кликнуть на чат
        if not token:
            print("Токен не получен, пробую взаимодействовать со страницей...")
            # Пробуем обновить страницу
            page.reload()
            time.sleep(5)

        browser.close()

    if not token:
        raise RuntimeError("Не удалось получить x-client-token. Проверьте логин/пароль.")

    return token


def save_token(token: str, filepath: str = "token.json"):
    """Сохраняет токен в файл."""
    data = {
        "x-client-token": token,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Токен сохранён в {filepath}")


def load_token(filepath: str = "token.json") -> str | None:
    """Загружает токен из файла."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get("x-client-token")
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    # Загружаем переменные окружения
    from dotenv import load_dotenv
    load_dotenv("env")

    login = os.environ.get("RETAILCRM_LOGIN")
    password = os.environ.get("RETAILCRM_PASSWORD")

    if not login or not password:
        raise RuntimeError("Не заданы RETAILCRM_LOGIN и RETAILCRM_PASSWORD")

    print(f"Логинимся как {login}...")
    token = get_retailcrm_token(login, password, headless=True)
    print(f"Получен токен: {token}")
    save_token(token)
