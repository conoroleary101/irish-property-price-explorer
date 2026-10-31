def test_pytest_is_working():
    assert 1 + 1 == 2

def test_deliberate_failure():
    assert False, "Proving CI catches failures"