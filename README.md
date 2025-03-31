# Slots Class

A modern, efficient object model using ```__slots__```.

Reap the performance benefits of slots-based objects while avoiding some of python's problematic dynamic behaviors.

## Installation

```pip install slots-class```

## Usage

Slots are assigned to the class statically at load time.

```python
>>> from slots_class import SlotsClass

>>> class MyObject(SlotsClass):
...     def __init__(self, x):
...         self.x = x
...         self.y = 10
...
...     def set_z(self, value):
...         self._z = value

>>> MyObject.__slots__
('_z', 'x', 'y')

```
