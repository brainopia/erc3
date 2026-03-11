from erc3_live.transport_contract import __doc__ as CONTRACT_NOTE


def test_transport_contract_note_mentions_ui_dispatch_route_shape():
    assert "/<api_root>/<task_id>/<endpoint>" in CONTRACT_NOTE
    assert "erc32.dispatch(window.apiRoot, window.currentTaskID, endpoint, body)" in CONTRACT_NOTE
    assert "POST /tasks/complete" in CONTRACT_NOTE
