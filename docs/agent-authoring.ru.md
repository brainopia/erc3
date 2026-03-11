# Как писать агента для этого репозитория

Читайте этот файл, если вы добавляете новый агент, меняете контракт agent entrypoint или готовите smoke-агента для проверок.

Если вы попали сюда напрямую без общего контекста, сначала откройте `AGENTS.md`, затем при необходимости `README.md`. Этот документ покрывает только агентный маршрут.

## Поддерживаемые entrypoint’ы

`erc3_live/runner.py` поддерживает два варианта.

### Предпочтительный

```python
def run_agent(task_client, task_info) -> None:
    ...
```

Аргументы:
- `task_client` — экземпляр `TaskClient`
- `task_info` — `PublicTaskRun`

Это основной и рекомендуемый контракт.

### Legacy-совместимый

```python
def solve(task_info, client) -> None:
    ...
```

`runner.py` адаптирует его к современному виду. Новые агенты так писать не нужно, но старые ещё поддерживаются.

## Что агент получает

### `task_info`

Из `PublicTaskRun` вам обычно полезны:
- `task_info.spec.spec_id`
- `task_info.spec.prompt`
- `task_info.runtime.task_id`
- `task_info.runtime.task_url`
- `task_info.runtime.api_root`

### `task_client`

Через него агент dispatch’ит task API. Для примеров смотрите:
- `examples/minimal_agent.py`
- `erc3_live/tests/e2e_agents.py`

## Минимальный шаблон

```python
def run_agent(task_client, task_info) -> None:
    identity = task_client.who_am_i()
    task_client.respond(
        message=f"Проверка для {task_info.runtime.task_id}",
        outcome="clarifying_question",
        links=[],
    )
```

Это не «хороший ERC3-агент». Это только корректный entrypoint для проверки обвязки.

## Что должен делать хороший агент в ERC3-контексте

Даже если код живёт вне этого репозитория, рабочая дисциплина почти всегда такая:

1. Сначала `/whoami`
2. Затем нужные wiki/project/employee/customer/time lookup’ы
3. Перед опасной мутацией — проверка прав
4. В конце — только структурированный `/respond`

См. `docs/erc3-scope.ru.md` и `docs/ERC3_RU_REPORT.md`.

## Failure path

Если агент бросает исключение, `runner.run_task_with_agent()` всё равно пытается корректно завершить задачу и возвращает результат со статусом `agent_failed`.

Это важно:
- исключение агента не означает, что можно пропустить completion
- если вы тестируете failure path, используйте `erc3_live/tests/failing_agent_fixture.py`

## Что не делать

- Не считайте примерный агент доказательством качества стратегии на всём ERC3.
- Не смешивайте wrapper-логику и соревновательную агентную стратегию без необходимости.
- Не пишите новый агент в legacy-форме `solve(...)`, если нет совместимости, которую реально надо сохранить.

## Где смотреть примеры

- `examples/minimal_agent.py` — самый короткий smoke-агент
- `erc3_live/tests/e2e_agents.py` — тестовый агент с `run_agent` и `solve`
- `erc3_live/tests/failing_agent_fixture.py` — намеренно падающий агент для проверки failure path

## Как проверять нового агента

Канонический набор уровней проверки и критериев достаточного доказательства собран в `docs/testing-and-verification.ru.md`. Ниже — минимальный агентный маршрут.

Минимум:

```bash
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli run-task --benchmark erc3-prod --spec t025 --agent path/to/agent.py
```

Если вы меняли ещё и runner/CLI, затем прогоните:

```bash
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/e2e/test_agent_flow.py erc3_live/tests/e2e/test_cli_flow.py -q
```