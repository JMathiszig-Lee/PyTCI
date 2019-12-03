import pytest
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

def test_eleveld():
    """ values from https://www.ncbi.nlm.nih.gov/pubmed/28509794 """
    testpatient = remifentanil.Eleveld(35, 70, 170, 'm')
    assert testpatient.v1 == 5.81
    assert testpatient.v2 == 8.82
    assert testpatient.v3 == 5.03

    assert testpatient.Q1 == 2.58
    assert testpatient.Q2 == 1.72
    assert testpatient.Q3 == 0.124

    with pytest.raises(ValueError):
        remifentanil.Eleveld(35, 70, 170, 'h')