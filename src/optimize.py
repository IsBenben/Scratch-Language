from nodes import *
import operator

from nodes import FunctionDeclaration

numeric_operators = {
    'operator_add': operator.add,
    'operator_subtract': operator.sub,
    'operator_multiply': operator.mul,
    'operator_divide': operator.truediv,
    'operator_mod': operator.mod,
}
comparison_operators = {
    'operator_gt': operator.gt,
    'operator_lt': operator.lt,
    'operator_equals': operator.eq,
}
logic_operators = {
    # operator.and_ and operator.or_ are bitwise operators
    'operator_and': lambda a, b: a and b,
    'operator_or': lambda a, b: a or b,
}

class Optimizer(NodeTransformer):
    def visit(self, node):
        # Example: !(!(!true)) -> false
        return super().visit(node)
    
    def visit_FunctionDeclaration(self, node):
        if 'nooptimize' in node.attributes:
            return None
        return super().visit_FunctionDeclaration(node)

    def visit_FunctionCall(self, node):
        super().visit_FunctionCall(node)
        if not node.always_builtin:
            return None
        
        if node.name in numeric_operators:
            if len(node.args) != 2:
                return None
            left, right = node.args
            if isinstance(left, Number) and isinstance(right, Number):
                return Number(numeric_operators[node.name](left.value, right.value))
        if node.name in comparison_operators:
            if len(node.args) != 2:
                return None
            left, right = node.args
            if isinstance(left, Number) and isinstance(right, Number):
                return create_boolean(comparison_operators[node.name](left.value, right.value))
        if node.name in logic_operators:
            if len(node.args) != 2:
                return None
            left, right = node.args
            if is_boolean(left) and is_boolean(right):
                return create_boolean(logic_operators[node.name](value_of_boolean(left), value_of_boolean(right)))
        if node.name == 'control_if':
            if len(node.args) != 2:
                return None
            condition, sub_stack = node.args
            if is_boolean(condition):
                return sub_stack if value_of_boolean(condition) else Block()
        if node.name == 'control_if_else':
            if len(node.args) != 3:
                return None
            condition, sub_stack, sub_stack2 = node.args
            if is_boolean(condition):
                return sub_stack if value_of_boolean(condition) else sub_stack2
        if node.name == 'control_repeat_until':
            if len(node.args) != 2:
                return None
            condition, sub_stack = node.args
            if is_boolean(condition):
                # until True -> pass
                # until False -> while True: sub_stack
                return Block() if value_of_boolean(condition) else FunctionCall(
                    'control_forever', [sub_stack]
                )
        if node.name == 'control_repeat':
            if len(node.args) != 2:
                return None
            times, sub_stack = node.args
            if isinstance(times, Number):
                if times.value < 1:
                    return Block()
                if times.value >= 10:
                    # Too many loops!
                    return None
                return Block([sub_stack] * int(times.value))
        if is_boolean(node):
            return create_boolean(node)
