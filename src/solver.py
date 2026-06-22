class TwentyFourSolver:
    def __init__(self):
        self.ops = ['+', '-', '*', '/']

    def solve(self, nums, target=24, find_all=False):
        """
        递归回溯求解
        :param nums: 数字列表
        :param target: 目标值
        :param find_all: 是否找出所有解
        :return: 解的列表
        """
        solutions = []
        # 结构: (float_value, string_expr, root_op, signature)
        # signature: 记录表达式的抽象结构，用于彻底去除加法和乘法交换律、结合律产生的等价重复解
        nums = [(float(n), self._format_num(n), None, ('n', str(n))) for n in nums]
        self._backtrack(nums, target, solutions, find_all)

        # 基于 signature 进行最终去重
        unique_solutions = {}
        for expr, sig in solutions:
            if sig not in unique_solutions:
                unique_solutions[sig] = expr
        return list(unique_solutions.values())

    def _backtrack(self, nums, target, solutions, find_all):
        if len(nums) == 1:
            if abs(nums[0][0] - target) < 1e-6:
                solutions.append((nums[0][1], nums[0][3]))  # (expr, signature)
            return

        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue

                a, expr_a, root_a, sig_a = nums[i]
                b, expr_b, root_b, sig_b = nums[j]
                remaining = [nums[k] for k in range(len(nums)) if k != i and k != j]

                for op in self.ops:
                    if op == '/' and abs(b) < 1e-6:
                        continue  # 避免除以零

                    # 剪枝：减少无谓的交换律计算，提升性能
                    if op in ['+', '*'] and i > j:
                        continue

                    new_val = self._calc(a, b, op)
                    new_sig = self._make_sig(op, sig_a, sig_b)

                    # 智能添加括号
                    left_str = self._add_parentheses(expr_a, root_a, op, is_left=True)
                    right_str = self._add_parentheses(expr_b, root_b, op, is_left=False)
                    new_expr = f"{left_str} {op} {right_str}"

                    self._backtrack(remaining + [(new_val, new_expr, op, new_sig)], target, solutions, find_all)

                    if not find_all and solutions:
                        return

    def _calc(self, a, b, op):
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a / b

    def _format_num(self, n):
        if n == int(n):
            return str(int(n))
        return str(n)

    def _make_sig(self, op, sig_a, sig_b):
        """
        生成表达式的规范化签名 (Signature)
        对于加法和乘法，会将所有操作数展平并排序，从而消除交换律和结合律带来的结构差异。
        """
        if op == '+':
            terms = []
            if sig_a[0] == '+':
                terms.extend(sig_a[1])
            else:
                terms.append(sig_a)
            if sig_b[0] == '+':
                terms.extend(sig_b[1])
            else:
                terms.append(sig_b)
            return ('+', tuple(sorted(terms)))
        elif op == '*':
            factors = []
            if sig_a[0] == '*':
                factors.extend(sig_a[1])
            else:
                factors.append(sig_a)
            if sig_b[0] == '*':
                factors.extend(sig_b[1])
            else:
                factors.append(sig_b)
            return ('*', tuple(sorted(factors)))
        else:
            return (op, sig_a, sig_b)

    def _add_parentheses(self, expr, root_op, current_op, is_left):
        """
        根据前后运算符的优先级决定是否加括号
        """
        if root_op is None:
            return expr

        current_prec = 1 if current_op in ['+', '-'] else 2
        root_prec = 1 if root_op in ['+', '-'] else 2

        # 情况1：子表达式优先级低，当前运算符优先级高，必须加括号 (如 (4+4)*4)
        if root_prec < current_prec:
            return f"({expr})"

        # 情况2：优先级相同
        if root_prec == current_prec:
            # 如果是左侧表达式，不需要加括号 (如 4+4+4)
            if is_left:
                return expr
            # 如果是右侧表达式，只有当当前运算符是 - 或 / 时，才需要加括号 (如 4-(4-4) 或 4/(4/4))
            if current_op in ['-', '/']:
                return f"({expr})"

        # 情况3：子表达式优先级高，不需要加括号 (如 4+4*4)
        return expr