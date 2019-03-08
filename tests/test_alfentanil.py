import pytest
from PyTCI.models import alfentanil

def test_maitre():
    testpatient = alfentanil.Maitre(30, 70, 170, 'm')

    assert round(testpatient.v1, 2) == 7.77
    assert round(testpatient.v2, 2) == 12.01
    assert round(testpatient.v3, 2) == 10.48
    assert round(testpatient.q1, 3) == 0.356
    
    with pytest.raises(ValueError):
        alfentanil.Maitre(20, 80, 180, 'g')