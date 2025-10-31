from custom_components.stiebel_eltron_http import dedupe


class FakeEntry:
    def __init__(self, entry_id, data=None, options=None, version=1, title="T", unique_id=None):
        self.entry_id = entry_id
        self.data = data or {}
        self.options = options or {}
        self.version = version
        self.title = title
        self.unique_id = unique_id


def test_plan_group_selects_most_complete_primary_and_find_keys_to_merge():
    # entry A has fewer keys; entry B has more and should become primary
    a = FakeEntry("a", data={"k1": 1}, options={"o1": 1}, version=1)
    b = FakeEntry("b", data={"k1": 1, "k2": 2}, options={"o1": 1, "o2": 2}, version=2)

    plan = dedupe.plan_group([a, b])
    # primary should be b (more complete)
    assert plan["primary"].entry_id == "b"

    # duplicate is 'a' and it has no keys that b doesn't already have
    assert len(plan["duplicates"]) == 1
    dup_plan = plan["duplicate_plans"][0]
    assert dup_plan["dup"].entry_id == "a"
    assert dup_plan["new_data_keys"] == []
    assert dup_plan["new_option_keys"] == []


def test_plan_group_detects_missing_keys_to_merge():
    # primary has some keys missing that duplicate holds
    # Give the primary more options so it scores higher by the planner heuristic
    primary = FakeEntry("p", data={"keep": 1}, options={"opt": 1, "a": 1, "b": 1}, version=5)
    dup = FakeEntry("d", data={"keep": 1, "extra": 7}, options={"opt": 1, "extra_opt": True}, version=1)

    plan = dedupe.plan_group([primary, dup])
    # primary remains 'p'
    assert plan["primary"].entry_id == "p"

    # duplicate plan should indicate keys to copy
    assert len(plan["duplicate_plans"]) == 1
    dp = plan["duplicate_plans"][0]
    assert dp["dup"].entry_id == "d"
    assert dp["new_data_keys"] == ["extra"]
    assert dp["new_option_keys"] == ["extra_opt"]
