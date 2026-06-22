import random
import json
import os
from solver import TwentyFourSolver
from evaluator import ExpressionEvaluator


class GameManager:
    def __init__(self):
        self.solver = TwentyFourSolver()
        self.evaluator = ExpressionEvaluator()
        self.high_score = self._load_high_score()
        self.current_score = 0
        self.level = 1

        # 拓展模式默认设置
        self.card_count = 4
        self.max_value = 13
        self.target = 24

    def _load_high_score(self):
        if os.path.exists('highscore.json'):
            try:
                with open('highscore.json', 'r') as f:
                    return json.load(f).get('high_score', 0)
            except:
                return 0
        return 0

    def _save_high_score(self):
        with open('highscore.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)

    def generate_valid_cards(self):
        """生成一定有解的卡牌组合"""
        while True:
            cards = [random.randint(1, self.max_value) for _ in range(self.card_count)]
            if self.solver.solve(cards, self.target, find_all=False):
                return cards

    def check_answer(self, cards, user_expr):
        is_valid, result = self.evaluator.validate_and_eval(user_expr, cards)
        if not is_valid:
            return False, f"输入无效: {result}"

        if abs(result - self.target) < 1e-6:
            self.current_score += 10 * self.level
            if self.current_score > self.high_score:
                self.high_score = self.current_score
                self._save_high_score()
            return True, "回答正确！"
        else:
            return False, f"计算结果为 {result}，不等于 {self.target}。"

    def level_up(self):
        """升级逻辑：仅增加得分倍率，不修改卡牌数量"""
        self.level += 1