import ast
import operator


class ExpressionEvaluator:
    def __init__(self):
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv
        }

    def validate_and_eval(self, expr, allowed_nums):
        """
        校验表达式并求值
        :param expr: 用户输入的表达式
        :param allowed_nums: 允许使用的数字列表 (已转换)
        """
        try:
            node = ast.parse(expr, mode='eval').body
        except SyntaxError:
            return False, "语法错误"

        used_nums = []
        val = self._eval_node(node, used_nums)

        if val is None:
            return False, "包含非法字符或操作"

        # 检查使用的数字是否合规
        allowed_sorted = sorted(allowed_nums)
        used_sorted = sorted(used_nums)
        if allowed_sorted != used_sorted:
            return False, f"必须且只能使用卡牌: {allowed_nums}，你使用了: {used_sorted}"

        return True, val

    def _eval_node(self, node, used_nums):
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                used_nums.append(node.value)
                return node.value
            return None
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, used_nums)
            right = self._eval_node(node.right, used_nums)
            if left is None or right is None:
                return None
            op_type = type(node.op)
            if op_type in self.operators:
                try:
                    return self.operators[op_type](left, right)
                except ZeroDivisionError:
                    return None
            return None
        elif isinstance(node, ast.UnaryOp):  # 处理负号
            operand = self._eval_node(node.operand, used_nums)
            if operand is None: return None
            if isinstance(node.op, ast.USub):
                return -operand
            return None
        return None