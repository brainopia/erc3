# Тестирование и верификация

Читайте этот файл, если запускаете проверки, меняете тесты или подтверждаете изменение поведения.

## Уровни проверок в этом репозитории

### 1. Быстрые локальные тесты

Покрывают:
- парсинг
- transport contract
- агрегацию

Команда:

```bash
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/test_parsing.py erc3_live/tests/test_transport_contract.py erc3_live/tests/test_aggregate.py -q
```

Когда обязательны:
- при любых изменениях в `parsing.py`
- при изменениях в `transport.py`, `public_sdk.py`, `aggregate.py`, `models.py`

### 2. Live E2E

Покрывают:
- listing публичных задач
- repeated start/complete
- dispatch в реальные endpoint’ы
- runner success/failure path
- CLI success/failure path

Команда:

```bash
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/e2e -q
```

Что нужно понимать:
- это не изолированные тесты
- они работают против реального ERC3
- падение может значить баг в коде, но может значить и изменение удалённого окружения
- такие тесты особенно чувствительны к правам, сетевым ошибкам и изменению benchmark data

### 3. Verification scripts

Используйте, когда нужен более читаемый smoke-вывод, чем у pytest.

#### Публичный task flow

```bash
mise exec python@3.12 -- .venv/bin/python scripts/verify_public_task_flow.py erc3-prod t025
```

Сценарий проверяет:
- list_public_tasks
- start_public_task
- task metadata
- read-only dispatch
- `/respond`
- completion

#### CLI flow

```bash
mise exec python@3.12 -- .venv/bin/python scripts/verify_cli_flow.py erc3-prod t025
```

Сценарий проверяет:
- `list-tasks`
- `run-task`
- JSON-структуру результата

### 4. Прямой CLI smoke

Используйте для быстрой регрессии пользовательского интерфейса:

```bash
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli list-tasks --benchmark erc3-prod
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli run-task --benchmark erc3-prod --spec t025 --agent examples/minimal_agent.py
```

## Как выбирать минимальный набор проверок

### Меняли только документацию

Достаточно:
- перечитать затронутые команды/пути в документации
- проверить, что ссылки на файлы существуют

### Меняли runtime/transport/public SDK

Обязательно:
1. быстрые локальные тесты
2. live E2E
3. `scripts/verify_public_task_flow.py`
4. residue-check на устаревшие имена и утверждения

### Меняли runner/CLI

Обязательно:
1. быстрые локальные тесты, если затронули shared модели/агрегацию
2. live E2E
3. `scripts/verify_cli_flow.py`
4. прямой CLI smoke

## Что считается хорошим доказательством изменения

Недостаточно:
- «код выглядит правильно»
- «типизация не ругается»
- «один локальный unit test прошёл»

Достаточно только вместе:
- изменённый код
- проверка той ветки поведения, которую вы меняли
- подтверждение, что не осталось старых имён/старой логики там, где делался cutover

## Частые причины ложных выводов

### 1. Считать live-проверку unit-тестом

Live E2E проверяет интеграцию с реальным ERC3, а не только ваш код.

### 2. Проверять только success path

Для `runner.py` и `cli.py` обязательно проверяйте и failure path агента.

### 3. Игнорировать residue-check

После переименования или cutover нужно отдельно искать старые имена по репозиторию. Иначе остаются мёртвые импорты, комментарии или документация.

### 4. Путать «wrapper работает» и «агент конкурентоспособен в ERC3»

Этот репозиторий проверяет корректность обвязки. Он не доказывает качество reasoning-стратегии агента на всём benchmark’е.
