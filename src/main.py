import sys
import os
import re

# 确保能正确导入 src 目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_manager import GameManager
from solver import TwentyFourSolver


def reset_default_settings(gm):
    """重置为默认设置：4张牌，最大13，目标24"""
    gm.card_count = 4
    gm.max_value = 13
    gm.target = 24


def parse_settings(gm, cmd_str):
    """
    智能解析命令行设置参数，兼容各种空格情况。
    支持: /set target=12, /set target = 12, /set count=5 max=20
    """
    if not cmd_str.startswith('/set'):
        return False, "未知命令"

    content = cmd_str[4:].strip()  # 去掉 /set 前缀

    # 如果只输入 /set 或 /set help，显示帮助
    if not content or content.lower() == 'help':
        return True, ("💡 /set 用法: 输入 参数=值 进行设置，多个参数可用空格或逗号分隔。\n"
                      "   可用参数: count(卡牌数, 建议2-7), max(最大值), target(目标值)\n"
                      "   示例: /set target=48\n"
                      "   示例: /set count = 5, max = 20")

    # 使用正则表达式提取所有 "键 = 值" 的组合，自动忽略中间的空格
    matches = re.findall(r'(\w+)\s*=\s*(\d+)', content)
    if not matches:
        return False, "⚠️ 格式错误，请使用 参数=值 的格式 (如: /set target=48)"

    updated_any = False
    for key, val in matches:
        try:
            if key == 'count':
                if not (2 <= int(val) <= 7):
                    return False, "⚠️ 卡牌数量应在 2 到 7 之间"
                gm.card_count = int(val)
                updated_any = True
            elif key == 'max':
                if int(val) < 1:
                    return False, "⚠️ 卡牌最大值必须大于 0"
                gm.max_value = int(val)
                updated_any = True
            elif key == 'target':
                gm.target = int(val)
                updated_any = True
            else:
                return False, f"⚠️ 未知参数: {key} (可用参数: count, max, target)"
        except ValueError:
            return False, f"⚠️ 参数值错误: {key}={val}，请输入整数"

    if updated_any:
        return True, "✅ 设置已更新"
    return False, "未识别到有效的设置参数"


def print_current_settings(gm):
    """打印当前参数设置"""
    print(f"📌 当前设置: 凑 {gm.target} 点 | {gm.card_count} 张牌 | 最大值 {gm.max_value}")


def solve_mode(gm):
    """求解模式：生成全部解法"""
    print("\n" + "=" * 30)
    print("=== 求解模式 ===")
    reset_default_settings(gm)  # 每次进入重置默认
    print_current_settings(gm)
    print("(输入 /set 可修改参数，输入 /back 返回主菜单)")

    while True:
        user_input = input("\n输入卡牌(逗号分隔): ").strip()
        if not user_input:
            continue
        if user_input == '/back':
            break

        if user_input.startswith('/set'):
            ok, msg = parse_settings(gm, user_input)
            print(msg)
            print_current_settings(gm)
            continue

        try:
            # 解析输入的数字
            cards = [float(x.strip()) if '.' in x else int(x.strip()) for x in user_input.split(',')]

            # 检查输入数量是否匹配
            if len(cards) != gm.card_count:
                print(f"⚠️ 警告: 当前设置需要 {gm.card_count} 张牌，你输入了 {len(cards)} 张。")

            solutions = gm.solver.solve(cards, gm.target, find_all=True)

            if solutions:
                # 去重并排序输出
                unique_sols = sorted(list(set(solutions)))
                print(f"✅ 共找到 {len(unique_sols)} 种解法：")
                for s in unique_sols:
                    print(f"  {s} = {gm.target}")
            else:
                print("❌ 无解！")
        except ValueError:
            print("⚠️ 输入格式有误，请确保输入的是用逗号分隔的数字。")
        except Exception as e:
            print(f"⚠️ 发生错误: {e}")


def play_mode(gm):
    """互动模式：程序出题，用户作答"""
    print("\n" + "=" * 30)
    print("=== 互动模式 ===")
    reset_default_settings(gm)  # 每次进入强制重置默认
    print_current_settings(gm)

    print("规则: 程序出题，你需输入由这组数字和 +-*/() 组成的表达式凑出目标值。")
    print("命令: /next(跳过) /show(看解) /back(退出) /set help(修改难度)")

    # 互动模式初始化得分与等级
    gm.current_score = 0
    gm.level = 1
    cards = gm.generate_valid_cards()

    while True:
        print("\n" + "-" * 30)
        print(f"【第 {gm.level} 关】 卡牌: {cards}")
        print_current_settings(gm)
        print(f"当前得分: {gm.current_score} | 历史最高: {gm.high_score}")

        user_input = input("请输入表达式: ").strip()
        if not user_input:
            continue

        if user_input == '/back':
            print("退出互动模式。")
            break
        elif user_input == '/next':
            print("跳过本题。")
            cards = gm.generate_valid_cards()
            continue
        elif user_input == '/show':
            sol = gm.solver.solve(cards, gm.target, find_all=False)
            if sol:
                print(f"💡 参考解法: {sol[0]}")
            else:
                print("💡 本题无解")
            cards = gm.generate_valid_cards()
            continue
        elif user_input.startswith('/set'):
            ok, msg = parse_settings(gm, user_input)
            print(msg)
            print_current_settings(gm)
            cards = gm.generate_valid_cards()  # 更新设置后重新发牌
            continue

        # 正常作答判定
        success, msg = gm.check_answer(cards, user_input)
        if success:
            print(f"✅ {msg}")
            gm.level_up()
            cards = gm.generate_valid_cards()
        else:
            print(f"❌ {msg} (可输入 /next 跳过或 /show 查看答案)")


def main():
    gm = GameManager()

    while True:
        print("\n" + "=" * 40)
        print("              24点算法求解器")
        print("=" * 40)
        print("1. 求解模式 (输入卡牌生成全部解法)")
        print("2. 互动模式 (程序出题用户作答)")
        print("3. 退出程序")

        choice = input("请选择模式 (1/2/3): ").strip()

        if choice == '1':
            solve_mode(gm)
        elif choice == '2':
            play_mode(gm)
        elif choice == '3':
            print("感谢使用，再见！")
            break
        else:
            print("⚠️ 无效选择，请重新输入。")


if __name__ == '__main__':
    main()