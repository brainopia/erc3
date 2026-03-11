# Поток выполнения и архитектура обёртки

Читайте этот файл, если меняете рантайм, transport, SDK, runner или CLI.

## Слои

### 1. `HttpRuntime`

Файл: `erc3_live/http_runtime.py`

Ответственность:
- держит `requests.Session`
- строит абсолютный URL
- выполняет `GET` и `POST`
- поднимает `TransportError` при HTTP-ошибке

Чего здесь нет:
- парсинга HTML
- task-логики
- fallback в браузер
- knowledge о `PublicTaskSpec` или `PublicTaskResult`

Это намеренно самый узкий слой.

### 2. `LiveTransport`

Файл: `erc3_live/transport.py`

Ответственность:
- получить список публичных задач
- стартовать задачу
- достать metadata task page
- dispatch’ить task-level endpoint’ы
- завершить задачу

Именно здесь происходит переход от «сырого HTTP» к моделям домена:
- HTML benchmark page -> `list[PublicTaskSpec]`
- `/tasks/start` + task page -> `PublicTaskRun`
- `/tasks/complete` -> `TaskCompletion`

### 3. `PublicERC3`

Файл: `erc3_live/public_sdk.py`

Ответственность:
- дать более удобный публичный интерфейс поверх transport
- создать `TaskClient` для уже стартованной задачи
- завершить задачу в форме `PublicTaskResult`
- агрегировать результаты

Текущее упрощение: `list_public_tasks()` кеширует полученные `PublicTaskSpec` по benchmark, а `start_public_task()` переиспользует кешированный spec, если listing уже был вызван ранее. Это убирает лишний повторный fetch benchmark page на каждый старт.

Важно: `start_public_task()` не обещает всегда иметь полный hydrated spec, если до этого listing не вызывали. В таком случае используется spec из start-response/task metadata потока.

### 4. `TaskClient`

Файл: `erc3_live/client.py`

Ответственность:
- дать агенту удобные методы для task dispatch
- держать связь с `PublicTaskRun`
- не знать про listing benchmark’ов или CLI

### 5. `runner.py`

Ответственность:
- загрузить агентный модуль по пути
- принять либо современный entrypoint `run_agent(task_client, task_info)`, либо legacy `solve(task_info, client)`
- прогнать одну задачу или список задач
- при исключении агента всё равно завершить задачу и вернуть `agent_failed`

Почему это важно:
- агентный модуль здесь недоверенный по отношению к wrapper-контракту
- runner должен быть понятным в failure path, потому что именно тут легко потерять completion и исказить диагностику

### 6. `cli.py`

Ответственность:
- разобрать CLI-аргументы
- вызвать один из трёх потоков: list, run-task, run-all
- печатать JSON как единственный публичный формат выхода

## Сквозной поток `run-task`

1. CLI читает аргументы.
2. `runner.load_agent_callable()` загружает агент.
3. `runner.run_task_with_agent()` вызывает `core.start_public_task()`.
4. `PublicERC3.start_public_task()` делегирует в `LiveTransport.start_public_task()`.
5. `LiveTransport.start_public_task()`:
   - POST `/tasks/start`
   - читает `/tasks/{task_id}`
   - парсит `api_root`
   - собирает `PublicTaskRun`
6. `PublicERC3.get_task_client()` создаёт `TaskClient`.
7. Агент вызывает методы `TaskClient`, которые уходят в `transport.dispatch()`.
8. После возврата или исключения агента `PublicERC3.complete_task()` вызывает `/tasks/complete` и собирает `PublicTaskResult`.
9. CLI печатает JSON.

## Где чаще всего ошибаются при изменениях

### Ошибка 1. Меняют transport без проверки parsing-контрактов

Следствие: wrapper получает task_id, api_root или completion status в неожиданной форме.

Проверять:
- `erc3_live/tests/test_parsing.py`
- `erc3_live/tests/test_transport_contract.py`
- `erc3_live/tests/e2e/test_sdk_flow.py`

### Ошибка 2. Ломают failure path агента

Следствие: задача стартует, агент падает, а completion не происходит или статус результата становится ложноположительным.

Проверять:
- `erc3_live/tests/e2e/test_agent_flow.py`
- `scripts/verify_cli_flow.py`

### Ошибка 3. Дублируют форматирование JSON в CLI-ветках

Следствие: разные команды дают несовместимые payload’ы или расходятся по сериализации.

Текущая норма: собрать `payload`, затем один раз вызвать `json.dumps(..., default=str)`.

### Ошибка 4. Тянут в `HttpRuntime` доменную логику

Это делает нижний слой ложной абстракцией. Если логика знает о `task_id`, `api_root`, `PublicTaskRun` или benchmark parsing, ей почти наверняка место выше.
