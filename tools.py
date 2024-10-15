from typing import Annotated, Literal

Operator = Literal["+", "-", "*", "/"]


def calculator(a: float, b: float, operator: Annotated[Operator, "operator"]) -> float:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return a / b
    else:
        raise ValueError("Invalid operator")

def esm_generate():
    pass