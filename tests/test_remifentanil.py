from PyTCI.models import remifentanil

def test_minto():
    testpatient = remifentanil.Minto(40, 80, 180, 'm')
    assert testpatient.v3 == 5.42
    assert testpatient.keo == 0.595