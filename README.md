# ERC3 live wrapper

Этот репозиторий — минимальная живая обёртка вокруг публичного ERC3 API и набор проверок для локальной разработки агентов. Он не решает задачи ERC3 «сам по себе». Его цель — дать предсказуемый HTTP-рантайм, тонкий SDK, CLI, live E2E-проверки и минимальный пример агента.

Для coding agents первый вход теперь `AGENTS.md`. Для людей этот `README.md` остаётся обзором проекта и human-readable картой маршрутов.

## С чего начать

Не читайте репозиторий подряд.

- Агент: начните с `AGENTS.md`, затем выберите ровно один профильный документ по задаче.
- Человек: используйте этот `README.md` как обзор проекта и карту дальнейшего чтения.
- К `docs/ERC3_RU_REPORT.md` переходите только если нужен широкий исследовательский контекст ERC3, а не локальное изменение wrapper.

## Читайте только следующий документ, который нужен под вашу задачу

- Нужно быстро понять, где что лежит и куда вносить изменения: `docs/project-map.ru.md`
- Нужно менять рантайм, SDK, CLI или поток выполнения задачи: `docs/runtime-flow.ru.md`
- Нужно запускать или добавлять проверки: `docs/testing-and-verification.ru.md`
- Нужно понять, что именно проверяет ERC3 и почему агент падает на обманчиво простых задачах: `docs/erc3-scope.ru.md`
- Нужно написать или адаптировать агента под этот репозиторий: `docs/agent-authoring.ru.md`
- Нужен полный исследовательский фон по ERC3, источникам и стратегиям: `docs/ERC3_RU_REPORT.md`

## Что есть в коде

- `erc3_live/public_sdk.py` — основной публичный вход: `PublicERC3`
- `erc3_live/client.py` — `TaskClient`, через который агент ходит в task API
- `erc3_live/transport.py` — HTTP-транспорт для list/start/dispatch/complete
- `erc3_live/http_runtime.py` — низкоуровневый HTTP-рантайм на `requests.Session`
- `erc3_live/runner.py` — загрузка агентного entrypoint и прогон задачи
- `erc3_live/cli.py` — команды `list-tasks`, `run-task`, `run-all`
- `erc3_live/tests/e2e/` — живые E2E-тесты против реального ERC3
- `scripts/verify_public_task_flow.py`, `scripts/verify_cli_flow.py` — ручные smoke/diagnostic сценарии
- `examples/minimal_agent.py` — минимальный агент для smoke-проверок

## Что важно помнить сразу

- В текущей версии рантайм только HTTP. Прежнего браузерного fallback-пути больше нет.
- `run-task` и live E2E нужны для проверки обёртки, а не для доказательства, что примерный агент конкурентоспособен в самом ERC3.
- ERC3 — это не только lookup. Бенчмарк проверяет права, мутации, формат ответа, `outcome`, `links`, неоднозначность, unsupported-ветки и корректное завершение через `/respond`.
- Если вы меняете публичный поток выполнения, проверяйте и код, и live E2E, и проверочные скрипты.

## Быстрый старт

### 1. Посмотреть список публичных задач

```bash
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli list-tasks --benchmark erc3-prod
```

### 2. Прогнать одну живую задачу через минимального агента

```bash
mise exec python@3.12 -- .venv/bin/python -m erc3_live.cli run-task --benchmark erc3-prod --spec t025 --agent examples/minimal_agent.py
```

### 3. Запустить быстрые локальные тесты обвязки

```bash
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/test_parsing.py erc3_live/tests/test_transport_contract.py erc3_live/tests/test_aggregate.py -q
```

### 4. Запустить live E2E

```bash
mise exec python@3.12 -- .venv/bin/python -m pytest erc3_live/tests/e2e -q
```

## Маршрут чтения для агента

1. Сначала `AGENTS.md`.
2. Затем выберите ровно один профильный документ из `docs/`.
3. Возвращайтесь к этому `README.md`, если нужен более подробный human-readable обзор проекта.
4. Переходите к коду только после выбора нужного маршрута.
5. К `docs/ERC3_RU_REPORT.md` идите только если нужен полный контекст соревнования, а не просто изменение обёртки.

Это сделано специально: ERC3 широкий по домену, но большинство задач сопровождения репозитория узкие. Сначала сузьте контекст, потом читайте глубже.