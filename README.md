# PyTCI

A python package for Target Controlled Infusions. 

Spawned from the NHS Hack Day project https://github.com/JMathiszig-Lee/Propofol, this splits out useful code into a package and updates it to python3

[![Build Status](https://travis-ci.org/JMathiszig-Lee/PyTCI.svg?branch=master)](https://travis-ci.org/JMathiszig-Lee/PyTCI)
[![Coverage Status](https://coveralls.io/repos/github/JMathiszig-Lee/PyTCI/badge.svg?branch=master)](https://coveralls.io/github/JMathiszig-Lee/PyTCI?branch=master)

# Installation


#Usage
PyTCI currently supports the following:

**Body Mass equations:**
* BMI
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

**Propofol models:**
* Schnider
* Marsh

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
        # Initial concentration is zero in all components
        self.x1 = 0.0
        self.x2 = 0.0
        self.x3 = 0.0
        self.xeo = 0.0

        #my custom code to generate volumes and constants


        # divide by 60 as we will be working in seconds
        self.k10 /= 60
        self.k12 /= 60
        self.k13 /= 60
        self.k21 /= 60
        self.k31 /= 60
        self.keo /= 60
```
