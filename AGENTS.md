# AGENTS.md

Этот файл — первый вход для coding agents.

Не читайте репозиторий подряд. Сначала выберите маршрут, потом открывайте ровно один профильный документ и только после этого идите в код.

Для людей подробный обзор проекта и расширенная карта чтения находятся в `README.md`.

## Быстрый маршрут

| Если задача про... | Сначала читать |
| --- | --- |
| где что лежит и какой файл менять | `docs/project-map.ru.md` |
| runtime, transport, SDK, runner, CLI, public execution flow | `docs/runtime-flow.ru.md` |
| проверки, smoke, pytest, verification | `docs/testing-and-verification.ru.md` |
| контракт агентного entrypoint или примеры агентов | `docs/agent-authoring.ru.md` |
| что реально проверяет ERC3 и почему «простые» задачи ломаются | `docs/erc3-scope.ru.md` |
| широкий исследовательский фон по ERC3 | `docs/ERC3_RU_REPORT.md` |

## Критические инварианты

- Этот репозиторий проверяет wrapper и live execution flow, а не доказывает, что агент конкурентоспособен на всём ERC3.
- ERC3 проверяет не только lookup: важны permissions, мутации, structured `/respond`, корректный `outcome`, `links`, ambiguity и unsupported-ветки.
- Если вы меняете public execution flow, недостаточно локального чтения кода: нужны соответствующие проверки из `docs/testing-and-verification.ru.md`.

## Команды входа

```bash
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli list-tasks --benchmark erc3-prod
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli run-task --benchmark erc3-prod --spec t025 --agent examples/minimal_agent.py
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/test_parsing.py erc3_live/tests/test_transport_contract.py erc3_live/tests/test_aggregate.py -q
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/e2e -q
```

## Правило чтения

1. Агент стартует отсюда.
2. Затем выбирает один профильный документ по задаче.
3. `README.md` читает как подробный human-readable обзор, а не как единственную точку входа.
4. `docs/ERC3_RU_REPORT.md` открывает только если нужен широкий контекст соревнования, а не локальное изменение wrapper.
