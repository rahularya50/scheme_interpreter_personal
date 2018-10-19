from typing import List

from datamodel import Expression, Number, bools
from environment import global_attr
from evaluate_apply import Frame
from gui import Holder
from helper import assert_all_numbers, verify_exact_callable_length
from primitives import BuiltIn, SingleOperandPrimitive
from scheme_exceptions import ComparisonError


@global_attr("+")
class Add(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        assert_all_numbers(operands)
        return Number(sum(operand.value for operand in operands))


@global_attr("-")
class Subtract(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        assert_all_numbers(operands)
        if len(operands) == 1:
            return Number(-operands[0].value)
        return Number(operands[0].value - sum(operand.value for operand in operands[1:]))


@global_attr("*")
class Multiply(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        assert_all_numbers(operands)
        out = 1
        for operand in operands:
            out *= operand.value
        return Number(out)


@global_attr("/")
class Divide(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        assert_all_numbers(operands)
        if len(operands) == 1:
            return Number(1 / operands[0].value)

        out = operands[0].value
        for operand in operands[1:]:
            out /= operand.value
        return Number(out)


@global_attr("abs")
class Abs(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return Number(abs(operand.value))


@global_attr("expt")
class Expt(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return Number(operands[0].value ** operands[1].value)


@global_attr("modulo")
class Modulo(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return Number(operands[0].value % abs(operands[1].value))


@global_attr("quotient")
class Quotient(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return Number(operands[0].value // operands[1].value)


@global_attr("remainder")
class Remainder(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return Number(operands[0].value % operands[1].value)


@global_attr("=")
class NumEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[operands[0].value == operands[1].value]


@global_attr("<")
class Less(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[operands[0].value < operands[1].value]


@global_attr("<=")
class LessOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[operands[0].value <= operands[1].value]


@global_attr(">")
class Greater(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[operands[0].value > operands[1].value]


@global_attr(">=")
class GreaterOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[operands[0].value >= operands[1].value]


@global_attr("even?")
class IsEven(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[not operand.value % 2]


@global_attr("odd?")
class IsOdd(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[operand.value % 2]


@global_attr("zero?")
class IsZero(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[operand.value == 0]