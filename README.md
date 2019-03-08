# PyTCI

A python package for Target Controlled Infusions. 

Spawned from the NHS Hack Day project https://github.com/JMathiszig-Lee/Propofol, this splits out useful code into a package and updates it to python3

[![Build Status](https://travis-ci.org/JMathiszig-Lee/PyTCI.svg?branch=master)](https://travis-ci.org/JMathiszig-Lee/PyTCI)
[![Coverage Status](https://coveralls.io/repos/github/JMathiszig-Lee/PyTCI/badge.svg?branch=master)](https://coveralls.io/github/JMathiszig-Lee/PyTCI?branch=master)

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

example:
```python
>>> from PyTCI.weights import leanbodymass
>>> leanbodymass.hume66(180, 60 'm')
51.2
```
**Models:**
**Propofol**
* Schnider
* Marsh
* Kataria
* Paedfusor

**Remifentanil**
* Minto

**Alfentanil**
*Maitre

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
7.9573934837092715
>>> patient.wait_time(60)
>>> patient.x1
6.179147869674185
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

