from app import store


class FakeCursor:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, fail_on_second=False, usage_row=None):
        self.calls = []
        self.fail_on_second = fail_on_second
        self.usage_row = {"n": 1} if usage_row is None else usage_row
        self.exit_exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.exit_exception = exc_type
        return False

    def execute(self, query, params=None):
        self.calls.append((query, params))
        if self.fail_on_second and len(self.calls) == 2:
            raise RuntimeError("recipe insert failed")
        return FakeCursor(self.usage_row)


def test_generated_recipe_and_quota_share_one_transaction(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(store, "db", lambda: connection)

    saved = store.save_generated_recipe(
        "user-1", "2026-11-15", 5, {"id": "recipe-1", "title": "Rice"}
    )

    assert saved is True
    assert len(connection.calls) == 2
    assert "insert into public.usage" in connection.calls[0][0]
    assert "insert into public.recipes" in connection.calls[1][0]
    assert connection.exit_exception is None


def test_recipe_insert_failure_rolls_back_quota_transaction(monkeypatch):
    connection = FakeConnection(fail_on_second=True)
    monkeypatch.setattr(store, "db", lambda: connection)

    import pytest
    with pytest.raises(RuntimeError, match="recipe insert failed"):
        store.save_generated_recipe(
            "user-1", "2026-11-15", 5, {"id": "recipe-1", "title": "Rice"}
        )

    assert len(connection.calls) == 2
    assert connection.exit_exception is RuntimeError


def test_exhausted_quota_does_not_insert_recipe(monkeypatch):
    connection = FakeConnection(usage_row=None)
    monkeypatch.setattr(store, "db", lambda: connection)

    saved = store.save_generated_recipe(
        "user-1", "2026-11-15", 5, {"id": "recipe-1", "title": "Rice"}
    )

    assert saved is False
    assert len(connection.calls) == 1
    assert connection.exit_exception is None
