# PyTCI

A python package for Target Controlled Infusions. 

Spawned from the NHS Hack Day project https://github.com/JMathiszig-Lee/Propofol, this splits out useful code into a package and updates it to python3

[![Build Status](https://travis-ci.org/JMathiszig-Lee/PyTCI.svg?branch=master)](https://travis-ci.org/JMathiszig-Lee/PyTCI)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyTCI)  
[![Coverage Status](https://coveralls.io/repos/github/JMathiszig-Lee/PyTCI/badge.svg?branch=master&kill_cache=1)](https://coveralls.io/github/JMathiszig-Lee/PyTCI?branch=master)
[![GitHub license](https://img.shields.io/github/license/JMathiszig-Lee/PyTCI)](https://github.com/JMathiszig-Lee/PyTCI/blob/master/license.txt)  
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/JMathiszig-Lee/PyTCI.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/JMathiszig-Lee/PyTCI/context:python)

# Installation
if using pip
```python
pip install PyTCI
```
if using pipenv (you should, it's great)
```python
pipenv install PyTCI
```
# Usage
PyTCI currently supports the following:

**Body Mass equations:**
* BMI
* Ideal body weight (Devine)
* Adjusted body weight
* James Equation
* Boer
* Hume(1966)
* Hume(1971)
* Janmahasation(2005)
* Al-Sallami

example:
```python
>>> from PyTCI.weights import leanbodymass
>>> leanbodymass.hume66(180, 60 'm')
51.2
```
# Models:
**Propofol**
* Schnider
* Marsh
* Eleveld
* Kataria
* Paedfusor

**Remifentanil**
* Minto
* Eleveld

**Alfentanil**
* Maitre

**Dexmedetomidine**
* Hannivoort
* Dyck
 
example:
```python
>>> from PyTCI.models import propofol
>>> patient = propofol.Schnider(40, 70, 170, 'm')
>>> patient.v2
24
```

the class methods ```give_drug``` and ```wait_time``` can he used to model propofol kinetics

example:
```python
>>> from PyTCI.models import propofol
>>> patient = propofol.Marsh(90)
>>> patient.give_drug(200)
>>> patient.x1
9.746588693957115
>>> patient.wait_time(60)
>>> patient.x1
7.438318565317236
```

**Infusions**

Infusions are currently only implemented for propofol

The two methods available are ```effect_bolus``` and ```plasma_infusion```

Effect bolus returns the bolus (in mg) needed over 10 seconds to achieve the desired effect site concentration. It's input is the desired target in ug/ml and returns the bolus needed in mg
```python
>>> patient = propofol.Schnider(40, 70, 190, 'm')
>>> patient.effect_bolus(6)
95.1
```
the function uses a simple search to find a dose that gets within 2% of the desired concentration 


Plasma_infusion takes desired plasma concentration(ug/ml), desired total time (seconds) and the time period for each segment (seconds) and returns a python list of the required infusions rates from every segment witin the total time specified in mg/sec
```python
>>> pt = propofol.Marsh(70)
>>> pt.plasma_infusion(2, 60)
[3.27269899102373, 0.1453355022895698, 0.14478000490919285, 0.14422948797801816, 0.1436839059972244, 0.143143213884116]
>>> pt.plasma_infusion(2, 60, 30)
[0.1420619352906052, 0.1417017659270992]

```



The built in models inherit from a parent class.
You can define your own models and use the same functions to see how yours performs
```python
class MyNewModel(Propofol):
     def __init__(self, desired, arguments):
        #my custom code to generate volumes and constants
        self.v1 = a_constant * weight
        self.v2 = a_constant * lean_body_mass
        etc... etc...

        #if you want to work with clearances rate constants must be generated
        self.from_clearances(self)

        #finally set up model 
        self.setup(self)

```

