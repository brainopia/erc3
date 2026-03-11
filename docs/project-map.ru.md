# Карта проекта

Читайте этот файл, если вам нужно быстро понять, где находится нужная логика и какой файл менять.

Если вы попали сюда напрямую без общего маршрута, начните с `AGENTS.md` (для агента) или `README.md` (для человека), а затем возвращайтесь сюда за картой файлов.

## Верхний уровень

- `AGENTS.md` — агентный entrypoint и короткий маршрутизатор по документации
- `README.md` — human-readable обзор проекта и карта маршрутов
- `docs/ERC3_RU_REPORT.md` — подробный исследовательский фон по соревнованию ERC3
- `examples/` — минимальные агенты и примеры запуска
- `scripts/` — ручные verification-сценарии
- `erc3_live/` — сам wrapper

## Пакет `erc3_live/`

### Публичные входы

- `erc3_live/__init__.py` — экспортируемая поверхность пакета
- `erc3_live/public_sdk.py` — класс `PublicERC3`; через него обычно начинают работу интеграции и тесты
- `erc3_live/cli.py` — CLI-команды для listing и запуска задач

### Выполнение задачи

- `erc3_live/runner.py` — загрузка агентного модуля, адаптация entrypoint (`run_agent` или legacy `solve`), прогон одной задачи или набора задач
- `erc3_live/client.py` — `TaskClient`, дружелюбная обёртка для task-level dispatch
- `erc3_live/transport.py` — HTTP-транспорт между SDK и публичным API ERC3
- `erc3_live/http_runtime.py` — самый нижний слой: `requests.Session`, `GET`, `POST`, базовый URL, обработка HTTP-ошибок

### Контракты и модели

- `erc3_live/models.py` — dataclass-модели task spec, run, result, summary
- `erc3_live/transport_contract.py` — контрактные вспомогательные сущности для transport слоя
- `erc3_live/errors.py` — собственные исключения

### Парсинг и агрегация

- `erc3_live/parsing.py` — HTML/JSON parsing для списка задач, task metadata и completion payload
- `erc3_live/aggregate.py` — сводка результатов по нескольким задачам

### Тесты

- `erc3_live/tests/test_parsing.py` — быстрые unit-проверки парсинга
- `erc3_live/tests/test_transport_contract.py` — контрактные проверки transport слоя
- `erc3_live/tests/test_aggregate.py` — проверки агрегирования
- `erc3_live/tests/e2e/` — живые интеграционные проверки против ERC3
- `erc3_live/tests/e2e/helpers.py` — общие helper’ы для live E2E
- `erc3_live/tests/e2e_agents.py` — тестовые агентные фикстуры
- `erc3_live/tests/failing_agent_fixture.py` — негативный агент для проверки error path

## Если меняете конкретную вещь

### Нужно поменять сетевой слой

Сначала читайте:
1. `docs/runtime-flow.ru.md`
2. `erc3_live/http_runtime.py`
3. `erc3_live/transport.py`
4. `erc3_live/tests/test_transport_contract.py`
5. `erc3_live/tests/e2e/test_sdk_flow.py`

### Нужно поменять старт/завершение задачи

Сначала читайте:
1. `docs/runtime-flow.ru.md`
2. `erc3_live/public_sdk.py`
3. `erc3_live/transport.py`
4. `erc3_live/runner.py`
5. `scripts/verify_public_task_flow.py`

### Нужно поменять CLI

Сначала читайте:
1. `erc3_live/cli.py`
2. `erc3_live/runner.py`
3. `erc3_live/tests/e2e/test_cli_flow.py`
4. `scripts/verify_cli_flow.py`

### Нужно поменять контракт агента

Сначала читайте:
1. `docs/agent-authoring.ru.md`
2. `erc3_live/runner.py`
3. `erc3_live/client.py`
4. `examples/minimal_agent.py`
5. `erc3_live/tests/e2e_agents.py`

### Нужно понять, почему live проверка падает на реальном ERC3

Сначала читайте:
1. `docs/testing-and-verification.ru.md`
2. `docs/erc3-scope.ru.md`
3. соответствующий файл в `erc3_live/tests/e2e/`
4. `scripts/verify_public_task_flow.py` или `scripts/verify_cli_flow.py`

## Что не перепутать

- `PublicERC3` — это wrapper для публичных задач, не полный session SDK для всего соревнования.
- `TaskClient` dispatch’ит task API, но итог задачи всё равно завершается через transport/public SDK поток.
- Live E2E бьют по реальному окружению; это не hermetic tests.
- Исследовательский отчёт описывает широкий ERC3-контекст, но не каждая его часть прямо реализована в этом репозитории.