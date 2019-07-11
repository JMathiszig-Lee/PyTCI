import pytest
from PyTCI.models import alfentanil

def test_maitre():
    testpatient = alfentanil.Maitre(30, 70, 170, 'm')
    testpatient2 = alfentanil.Maitre(60, 80, 165, 'f')

    assert round(testpatient.v1, 2) == 7.77
    assert round(testpatient.v2, 2) == 12.01
    assert round(testpatient.v3, 2) == 10.48
    assert round(testpatient.q1, 3) == 0.356
    
    assert round(testpatient2.v1, 2) == 10.24

    with pytest.raises(ValueError):
        alfentanil.Maitre(20, 80, 180, 'g')