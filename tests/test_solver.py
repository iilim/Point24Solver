import sys
import os
import unittest

# 动态添加 src 目录到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.solver import TwentyFourSolver
from src.evaluator import ExpressionEvaluator
from src.game_manager import GameManager


class TestSolver(unittest.TestCase):
    """核心求解器测试"""

    def setUp(self):
        self.solver = TwentyFourSolver()

    def test_known_solvable(self):
        """已知有解的组合"""
        test_cases = [
            [1, 2, 3, 4],
            [8, 3, 8, 3],  # 8/(3-8/3)=24
            [6, 6, 6, 6],  # 6+6+6+6=24
            [3, 3, 8, 8],  # 8/(3-8/3)=24 变体
            [1, 5, 5, 5],  # (5-1/5)*5=24
        ]
        for nums in test_cases:
            with self.subTest(nums=nums):
                solutions = self.solver.solve(nums, target=24, find_all=True)
                self.assertGreater(len(solutions), 0, f"{nums} 应该有解")

    def test_known_unsolvable(self):
        """已知无解的组合"""
        unsolvable = [
            [1, 1, 1, 1],
            [1, 1, 1, 2],
            [2, 2, 2, 2],  # 四个数全相同且无法组合成24
        ]
        for nums in unsolvable:
            with self.subTest(nums=nums):
                solutions = self.solver.solve(nums, target=24, find_all=True)
                self.assertEqual(len(solutions), 0, f"{nums} 应该无解，但找到: {solutions[:3]}")

    def test_get_one_solution(self):
        """获取单个解 (find_all=False)"""
        sols = self.solver.solve([1, 2, 3, 4], find_all=False)
        self.assertEqual(len(sols), 1, "find_all=False 时应只返回一个解")

        # 无解时应返回空列表
        sols = self.solver.solve([1, 1, 1, 1], find_all=False)
        self.assertEqual(len(sols), 0)

    def test_solution_uniqueness(self):
        """解的去重：验证 AST 签名去重机制是否生效"""
        # 4,4,4,4 在数学上只有一种本质解：4*4+4+4
        solutions = self.solver.solve([4, 4, 4, 4], target=24, find_all=True)
        self.assertEqual(len(solutions), 1, f"4,4,4,4 应该只有1种去重后的解，实际得到: {solutions}")

    def test_custom_target(self):
        """拓展模式：自定义目标值"""
        # 1,2,3 凑 6
        solutions = self.solver.solve([1, 2, 3], target=6, find_all=True)
        self.assertGreater(len(solutions), 0, "[1,2,3] 凑 6 应该有解")

    def test_no_redundant_parentheses(self):
        """智能括号：确保不生成冗余括号"""
        solutions = self.solver.solve([1, 2, 3, 4], find_all=True)
        for sol in solutions:
            # 检查是否不存在类似 ((1+2))+3 这样的连续双括号
            self.assertNotIn("((", sol, f"表达式中存在冗余的连续左括号: {sol}")


class TestEvaluator(unittest.TestCase):
    """表达式求值器与安全校验测试"""

    def setUp(self):
        self.ev = ExpressionEvaluator()

    def test_correct_calculation(self):
        """基本计算与括号优先级"""
        # validate_and_eval 返回 (bool, result_or_msg)
        valid, res = self.ev.validate_and_eval("(1+2)*3", [1, 2, 3])
        self.assertTrue(valid)
        self.assertEqual(res, 9.0)

    def test_invalid_characters(self):
        """非法字符拦截 (防止代码注入)"""
        valid, msg = self.ev.validate_and_eval("__import__('os').system('rm -rf /')", [1, 2])
        self.assertFalse(valid)
        self.assertIn("非法字符", msg)

    def test_division_by_zero(self):
        """除以零拦截"""
        valid, msg = self.ev.validate_and_eval("1/0", [1, 0])
        self.assertFalse(valid)
        # 内部捕获了 ZeroDivisionError，返回 None，被外层判定为非法
        self.assertIn("非法", msg)

    def test_wrong_numbers(self):
        """防作弊：使用了不在题目中的数字"""
        # 题目是 [1,2,3,4]，但表达式用了 8
        valid, msg = self.ev.validate_and_eval("(1+2)*8", [1, 2, 3, 4])
        self.assertFalse(valid)
        self.assertIn("必须且只能使用卡牌", msg)

    def test_reuse_number(self):
        """防作弊：重复使用数字"""
        # 题目是 [3,8,1,2]，但 3 被使用了两次
        valid, msg = self.ev.validate_and_eval("3*3+8-1", [3, 8, 1, 2])
        self.assertFalse(valid)
        self.assertIn("必须且只能使用卡牌", msg)


class TestGameManager(unittest.TestCase):
    """游戏管理器测试"""

    def setUp(self):
        # 为了避免污染真实的 highscore.json，可以使用临时 mock
        self.gm = GameManager()
        self.gm.high_score = 0
        self.gm.current_score = 0

    def test_generate_valid_cards_default(self):
        """默认设置下生成的牌一定有解且符合数量"""
        cards = self.gm.generate_valid_cards()
        self.assertEqual(len(cards), 4)
        self.assertTrue(all(1 <= c <= 13 for c in cards))

        # 验证确实有解
        sols = self.gm.solver.solve(cards, 24, find_all=False)
        self.assertGreater(len(sols), 0)

    def test_generate_valid_cards_custom(self):
        """拓展模式：自定义参数下的发牌"""
        self.gm.card_count = 5
        self.gm.max_value = 20
        self.gm.target = 100

        cards = self.gm.generate_valid_cards()
        self.assertEqual(len(cards), 5)
        self.assertTrue(all(1 <= c <= 20 for c in cards))

        # 验证在自定义参数下确实有解
        sols = self.gm.solver.solve(cards, 100, find_all=False)
        self.assertGreater(len(sols), 0)

    def test_check_answer_correct(self):
        """测试答对时的得分逻辑"""
        self.gm.target = 24
        cards = [4, 4, 4, 4]
        success, msg = self.gm.check_answer(cards, "4*4+4+4")
        self.assertTrue(success)
        self.assertEqual(self.gm.current_score, 10)  # 10 * level(1)

    def test_check_answer_wrong(self):
        """测试答错时不加分"""
        self.gm.target = 24
        cards = [1, 2, 3, 4]
        success, msg = self.gm.check_answer(cards, "1+2+3+4")
        self.assertFalse(success)
        self.assertEqual(self.gm.current_score, 0)


if __name__ == '__main__':
    unittest.main()