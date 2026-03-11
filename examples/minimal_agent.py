def run_agent(task_client, task_info):
    identity = task_client.who_am_i()
    message = f"Task {task_info.runtime.task_id} via {task_info.runtime.dispatch_via or 'unknown'}"
    task_client.respond(message=message, outcome="clarifying_question", links=[])
    return identity
