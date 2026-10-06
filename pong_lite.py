"""pong-lite: 最小乒乓球模拟器。纯标准库,无实时输入,只有无头演示。

物理模型:球有速度 (vx, vy);撞上下墙翻转 vy;撞挡板翻转 vx 并按击球位置
给出 vy(越偏离中心 vy 越大);错过挡板对方得分。
"""

import argparse
import random
import sys

WIDTH = 40
HEIGHT = 16
PADDLE_H = 4
BALL_SPEED = 1.0
MAX_VY = 1.6


class Pong:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.score_l = 0
        self.score_r = 0
        self.reset()

    def reset(self):
        self.pad_l = HEIGHT // 2          # 挡板中心 y
        self.pad_r = HEIGHT // 2
        self.ball_x = WIDTH / 2
        self.ball_y = HEIGHT / 2
        angle = self.rng.uniform(-0.6, 0.6)
        direction = self.rng.choice((-1, 1))
        self.vx = BALL_SPEED * direction
        self.vy = BALL_SPEED * angle * direction * 2

    def _paddle_bounce(self, side):
        """挡板反弹。hit=-1(下沿)..+1(上沿),vy 与偏离同向。"""
        pad = self.pad_l if side == "L" else self.pad_r
        hit = (self.ball_y - pad) / (PADDLE_H / 2)
        hit = max(-1.0, min(1.0, hit))
        self.vx = -self.vx
        self.vy = MAX_VY * hit

    def step(self):
        """推进一步,返回事件:'wall'|'paddleL'|'paddleR'|'scoreL'|'scoreR'|None。"""
        self.ball_x += self.vx
        self.ball_y += self.vy
        ev = None

        if self.ball_y <= 0:
            self.ball_y = 0
            self.vy = -self.vy
            ev = "wall"
        elif self.ball_y >= HEIGHT - 1:
            self.ball_y = HEIGHT - 1
            self.vy = -self.vy
            ev = "wall"

        if self.vx < 0 and self.ball_x <= 1:
            if abs(self.ball_y - self.pad_l) <= PADDLE_H / 2:
                self.ball_x = 1
                self._paddle_bounce("L")
                ev = "paddleL"
            elif self.ball_x < 0:
                self.score_r += 1
                self.reset()
                return "scoreR"
        elif self.vx > 0 and self.ball_x >= WIDTH - 2:
            if abs(self.ball_y - self.pad_r) <= PADDLE_H / 2:
                self.ball_x = WIDTH - 2
                self._paddle_bounce("R")
                ev = "paddleR"
            elif self.ball_x > WIDTH - 1:
                self.score_l += 1
                self.reset()
                return "scoreL"
        return ev

    def ai_move(self, max_speed=1.0):
        """双方 AI:挡板以有限速度追踪球 y(靠近自己半区才追)。"""
        for side in ("L", "R"):
            approaching = (self.vx < 0) == (side == "L")
            target = self.ball_y if approaching else HEIGHT / 2
            pad = self.pad_l if side == "L" else self.pad_r
            diff = target - pad
            move = max(-max_speed, min(max_speed, diff))
            pad = max(PADDLE_H / 2, min(HEIGHT - 1 - PADDLE_H / 2, pad + move))
            if side == "L":
                self.pad_l = pad
            else:
                self.pad_r = pad

    def render(self):
        rows = []
        for y in range(HEIGHT):
            line = [" "] * WIDTH
            line[0] = "|"
            line[WIDTH - 1] = "|"
            for dy in range(-PADDLE_H // 2, PADDLE_H // 2 + 1):
                for x, pad in ((1, self.pad_l), (WIDTH - 2, self.pad_r)):
                    if int(round(pad)) + dy == y:
                        line[x] = "#"
            bx, by = int(round(self.ball_x)), int(round(self.ball_y))
            if 0 <= bx < WIDTH and 0 <= by < HEIGHT:
                line[bx] = "o"
            rows.append("".join(line))
        return "\n".join(rows)


def auto_demo(seed=None, rallies=200, ai_speed=1.0, show=False):
    g = Pong(seed)
    for i in range(rallies * 40):
        g.ai_move(ai_speed)
        ev = g.step()
        if show and ev in ("scoreL", "scoreR"):
            print(f"\n--- 回合 {g.score_l + g.score_r} ({ev}) ---")
            print(g.render())
        if g.score_l + g.score_r >= rallies:
            break
    return g.score_l, g.score_r


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pong-lite", description="最小乒乓球模拟器(无头演示)。")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--rallies", type=int, default=20, help="演示回合数")
    ap.add_argument("--ai-speed", type=float, default=1.0, help="AI 挡板最大速度")
    ap.add_argument("--show", action="store_true", help="每次得分打印棋盘")
    ap.add_argument("--auto", action="store_true", help="运行无头演示")
    args = ap.parse_args(argv)

    if not args.auto:
        print("pong-lite 是无头模拟器:请用 --auto 运行演示(无实时键盘输入)。")
        return 2
    sl, sr = auto_demo(args.seed, args.rallies, args.ai_speed, args.show)
    print(f"\n演示结束:左 {sl} : {sr} 右")
    return 0


if __name__ == "__main__":
    sys.exit(main())
