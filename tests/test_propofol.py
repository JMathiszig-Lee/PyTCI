from PyTCI.models import propofol
#source for values in marsh and schnider independantly derived https://academic.oup.com/view-large/91165989

def test_schnider():
    testpatient = propofol.Schnider(40, 70, 170, 'm')
    assert round(testpatient.v2) == 24
    # assert testpatient.k10 == (0.384 /60)
    # assert testpatient.k12 == 0.375
    # assert testpatient.k21== 0.067

    testpatient.give_drug(200)
    assert round(testpatient.x1, 2) == 46.84

    for _ in range(60):
        testpatient.wait_time(1)
    assert round(testpatient.x1, 2) == 22.03

def test_marsh():
    testpatient = propofol.Marsh(70)

    assert round(testpatient.v1, 1) == 16.0
    assert round(testpatient.v2, 1) == 32.4
    assert round(testpatient.v3, 1) == 202.5

# values for paediatric tests are from:
# Constant, Isabelle & Rigouzzo, Agnes. (2010). Which model for propofol TCI in children. 
# Paediatric anaesthesia. 20. 233-9. 10.1111/j.1460-9592.2010.03269.x.

def test_kataria():
    testchild = propofol.Kataria(20, 6)

    assert testchild.v1 == 7.6
    assert testchild.v2 == 17.4
    assert testchild.v3 == 122.4

    assert testchild.Q1 == 0.74
    assert testchild.Q2 == 1.26
    assert testchild.Q3 == 0.5

    #test warnings
    assert propofol.Kataria(10, 13)

def test_paedfusor():
    testchild = propofol.Paedfusor(20, 6)

    assert round(testchild.v1,1) == 9.2
    assert testchild.v2 == 19
    assert testchild.v3 == 117.0

    testk10 = 0.0624 /60
    assert round(testchild.k10, 5) == testk10

    #test warnings
    assert propofol.Paedfusor(10, 16)
    assert propofol.Paedfusor(10, 0.5)