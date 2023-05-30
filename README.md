# 2D Geometric Constraint Solver

![](./screenshots/demo.gif)

This project is an attempt to utilize [mathematical optimization algorithms](https://en.wikipedia.org/wiki/Mathematical_optimization), specifically [SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html), to deal with [geometric constraint solving](https://en.wikipedia.org/wiki/Geometric_constraint_solving) problem.

Currently, the project is not stable and mature enough to be considered seriously, but you can still experiment with it.

## How to run

```
pip install -r requirements.txt
python src/main.py
```

## How to use

1. Use the buttons on the left to add a new segment or an arc
2. Left click the point/segment/arc to select it
3. Click on an empty space to clear the selection
4. The available constraints are automatically displayed for the selected items. Left click the constraint button on the right to apply the constraint
5. To delete a segment or an arc, select it and press DELETE
6. To remove a constraint, left click its icon and press DELETE