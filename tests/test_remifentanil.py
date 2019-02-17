from PyTCI.models import remifentanil

def test_minto():
    testpatient = remifentanil.Minto(40, 80, 180, 'm')
    assert testpatient.v3 == 5.42
    assert round(testpatient.keo, 4) == 0.0099

    testpatient.give_drug(50)
    assert round(testpatient.x1, 2) == 8.84

    for _ in range(60):
        testpatient.wait_time(1)
    assert round(testpatient.x1, 2) == 3.88