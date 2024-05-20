import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 设置屏幕大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fireworks")

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 加载背景图片
background = pygame.image.load('D:\GitHub\LEARN_LLM\\beijing.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# 加载字体
font = pygame.font.Font('c:\WINDOWS\Fonts\STXINGKA.TTF', 60)

# 定义烟花粒子类
class Particle:
    def __init__(self, x, y, explosion=False):
        self.x = x
        self.y = y
        self.color = self.random_color()
        self.radius = random.randint(2, 6)  # 调整粒子大小范围
        if not explosion:
            self.vx = 0
            self.vy = random.uniform(-10, -15)  # 调整烟花爆炸的上升速度范围
        else:
            self.vx = random.uniform(-5, 5)  # 调整烟花爆炸的速度范围
            self.vy = random.uniform(-5, 5)  # 调整烟花爆炸的上升速度范围
        self.gravity = 0.2  # 调整烟花爆炸的重力影响
        self.alpha = 255
        self.explosion = explosion

    def random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.alpha -= 5  # 调整粒子的消失速度

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# 主函数
def main():
    fireworks = []

    clock = pygame.time.Clock()
    FPS = 60
    running = True

    while running:
        screen.blit(background, (0, 0))

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 发射烟花
        if random.randint(1, 60) == 1:
            x = random.randint(0, WIDTH)
            y = random.randint(HEIGHT // 2, HEIGHT)  # 调整烟花爆炸的位置
            firework = Particle(x, y)
            fireworks.append(firework)

        # 更新和绘制烟花
        for firework in fireworks:
            firework.update()
            firework.draw(screen)
            if firework.explosion:
                if firework.alpha <= 0:
                    fireworks.remove(firework)
            else:
                if firework.vy >= 0:
                    explosion_size = random.randint(40, 80)  # 调整爆炸粒子的数量范围
                    for _ in range(explosion_size):
                        particle = Particle(firework.x, firework.y, explosion=True)
                        fireworks.append(particle)
                    fireworks.remove(firework)

        # 在屏幕下半部分绘制文字
        text = font.render("新年快乐！", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
