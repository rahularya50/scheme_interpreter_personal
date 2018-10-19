from typing import List

from datamodel import Expression, Symbol, Pair, SingletonTrue, SingletonFalse, Nil
from environment import global_attr
from gui import Holder, VisualExpression
from helper import pair_to_list, verify_exact_callable_length, verify_min_callable_length, \
    make_list
from evaluate_apply import Frame, evaluate, Callable, evaluate_all
from scheme_exceptions import OperandDeduceError


class LambdaObject(Callable):
    def __init__(self, params: List[Symbol], body: List[Expression], frame: Frame):
        self.params = params
        self.body = body
        self.frame = frame

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        new_frame = Frame(self.frame)
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        gui_holder.apply()

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.base_expr) for expr in self.body])
        for i, expression in enumerate(self.body):
            out = evaluate(expression, new_frame, gui_holder.expression.children[i])
        return out

    def __repr__(self):
        return "#[lambda_obj]"


@global_attr("lambda")
class Lambda(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if isinstance(params, Symbol):
            params = [operands[0]]
        elif isinstance(params, Pair) or params is Nil:
            params = pair_to_list(params)
        else:
            raise OperandDeduceError(f"{params} is neither a Symbol or a List (aka Pair) of Symbols.")
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")
        if len(operands) == 2:
            # noinspection PyTypeChecker
            return LambdaObject(params, operands[1:], frame)
        else:
            # noinspection PyTypeChecker
            return LambdaObject(params, [Pair(Symbol("begin"), make_list(operands[1:]))], frame)


@global_attr("define")
class Define(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        first = operands[0]
        if isinstance(first, Symbol):
            verify_exact_callable_length(self, 2, len(operands))
            frame.assign(first, evaluate(operands[1], frame, gui_holder.expression.children[2]))
            return first
        elif isinstance(first, Pair):
            name = first.first
            operands[0] = first.rest
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected a Symbol, not {name}.")
            frame.assign(name, Lambda().execute(operands, frame, gui_holder))
            return name
        else:
            raise OperandDeduceError("Expected a Symbol or List (aka Pair) as first operand of define.")


@global_attr("if")
class If(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        if len(operands) > 3:
            verify_exact_callable_length(self, 3, len(operands))
        if evaluate(operands[0], frame, gui_holder.expression.children[1]) is SingletonFalse:
            if len(operands) == 2:
                return Nil
            else:
                # gui_holder.expression = gui_holder.expression.children[3].expression
                return evaluate(operands[2], frame, gui_holder.expression.children[3])
        else:
            # gui_holder.expression = gui_holder.expression.children[1].expression
            return evaluate(operands[1], frame, gui_holder.expression.children[2])


@global_attr("begin")
class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        out = None
        for operand, holder in zip(operands, gui_holder.expression.children[1:]):
            out = evaluate(operand, frame, holder)
        return out

    def __repr__(self):
        return "#[begin]"


@global_attr("quote")
class Quote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return operands[0]


@global_attr("eval")
class Eval(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        operand = evaluate(operands[0], frame, gui_holder.expression.children[1])
        gui_holder.expression = VisualExpression(operands[0], gui_holder.expression.base_expr)

        return evaluate(operand, frame, gui_holder)


@global_attr("cond")
class Cond(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for cond_i, cond in enumerate(operands):
            if not isinstance(cond, Pair):
                raise OperandDeduceError(f"Unable to evaluate clause of cond, as {cond} is not a Pair.")
            expanded = pair_to_list(cond)
            cond_holder = gui_holder.expression.children[cond_i + 1]
            verify_min_callable_length(self, 2, len(expanded))
            cond_holder.link_visual(VisualExpression(cond))
            if isinstance(expanded[0], Symbol) and expanded[0].value == "else" or evaluate(expanded[0], frame, cond_holder.expression.children[0]) is not SingletonFalse:
                out = None
                for i, expr in enumerate(expanded[1:]):
                    out = evaluate(expr, frame, cond_holder.expression.children[i + 1])
                return out
        return Nil


@global_attr("and")
class And(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1])
            if value is SingletonFalse:
                return SingletonFalse
        return SingletonTrue


@global_attr("or")
class Or(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1])
            if value is SingletonTrue:
                return SingletonTrue
        return SingletonFalse


@global_attr("let")
class Let(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))

        bindings = operands[0]
        if not isinstance(bindings, Pair) and bindings is not Nil:
            raise OperandDeduceError(f"Expected first argument of let to be a Pair, not {bindings}.")

        new_frame = Frame(frame)

        gui_holder.expression.children[1].link_visual(VisualExpression(bindings))
        bindings_holder = gui_holder.expression.children[1]

        bindings = pair_to_list(bindings)

        for i, binding in enumerate(bindings):
            if not isinstance(binding, Pair):
                raise OperandDeduceError(f"Expected binding to be a Pair, not {binding}.")
            binding_holder = bindings_holder.expression.children[i]
            binding_holder.link_visual(VisualExpression(binding))
            binding = pair_to_list(binding)
            if len(binding) != 2:
                raise OperandDeduceError(f"Expected binding to be of length 2, not {len(binding)}.")
            name, expr = binding
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected first element of binding to be a Symbol, not {name}.")
            new_frame.assign(name, evaluate(expr, frame, binding_holder.expression.children[1]))

        operands = evaluate_all(operands[1:], new_frame, gui_holder.expression.children[2:])

        return operands[-1]


@global_attr("mu")
class Mu(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if isinstance(params, Symbol):
            params = [operands[0]]
        elif isinstance(params, Pair) or params is Nil:
            params = pair_to_list(params)
        else:
            raise OperandDeduceError(f"{params} is neither a Symbol or a List (aka Pair) of Symbols.")
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")
        if len(operands) == 2:
            # noinspection PyTypeChecker
            return MuObject(params, operands[1:])
        else:
            # noinspection PyTypeChecker
            return MuObject(params, [Pair(Symbol("begin"), make_list(operands[1:]))])


class MuObject(Callable):
    def __init__(self, params: List[Symbol], body: List[Expression]):
        self.params = params
        self.body = body

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        new_frame = Frame(frame)
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        gui_holder.apply()

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.base_expr) for expr in self.body])
        for i, expression in enumerate(self.body):
            out = evaluate(expression, new_frame, gui_holder.expression.children[i])
        return out

    def __repr__(self):
        return "#[mu_obj]"


class MacroObject(Callable):
    def __init__(self, params: List[Symbol], body: List[Expression], frame: Frame):
        self.params = params
        self.body = body
        self.frame = frame

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        new_frame = Frame(self.frame)
        # operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.base_expr) for expr in self.body])
        for i, expression in enumerate(self.body):
            out = evaluate(expression, new_frame, gui_holder.expression.children[i])

        gui_holder.expression.set_entries([VisualExpression(out, gui_holder.expression.base_expr)])
        out = evaluate(out, frame, gui_holder.expression.children[i])
        return out

    def __repr__(self):
        return "#[macro_obj]"


@global_attr("define-macro")
class DefineMacro(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if not isinstance(params, Pair):
            raise OperandDeduceError(f"Expected a Pair, not {params}, as the first operand of define-macro.")
        params = pair_to_list(params)
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")
        name, *params = params
        if len(operands) == 2:
            # noinspection PyTypeChecker
            frame.assign(name, MacroObject(params, operands[1:], frame))
        else:
            # noinspection PyTypeChecker
            frame.assign(name, MacroObject(params, [Pair(Symbol("begin"), make_list(operands[1:]))], frame))
        return name