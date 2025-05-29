from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
import random


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)

        # 游戏设置
        self.cell_size = min(Window.width, Window.height) // 20  # 自适应屏幕大小
        self.board_width = Window.width // self.cell_size
        self.board_height = Window.height // self.cell_size

        # 游戏状态
        self.reset_game()

        # UI元素
        self.setup_ui()

        # 绑定事件
        Window.bind(on_key_down=self.on_keyboard_down)
        self.bind(on_touch_down=self.on_touch_down)

        # 开始游戏循环
        self.game_clock = None
        self.start_game()

    def setup_ui(self):
        """设置UI界面"""
        # 分数标签
        self.score_label = Label(
            text=f'分数: {self.score}',
            size_hint=(None, None),
            size=(200, 50),
            pos=(10, Window.height - 60),
            color=(1, 1, 1, 1),
            font_size='20sp'
        )
        self.add_widget(self.score_label)

        # 最高分标签
        self.high_score_label = Label(
            text=f'最高分: {self.high_score}',
            size_hint=(None, None),
            size=(200, 50),
            pos=(10, Window.height - 110),
            color=(1, 1, 0.5, 1),
            font_size='16sp'
        )
        self.add_widget(self.high_score_label)

        # 暂停按钮
        self.pause_btn = Button(
            text='暂停',
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 110, Window.height - 60)
        )
        self.pause_btn.bind(on_press=self.toggle_pause)
        self.add_widget(self.pause_btn)

        # 游戏说明
        self.info_label = Label(
            text='滑动屏幕或使用方向键控制',
            size_hint=(None, None),
            size=(300, 30),
            pos=(Window.width // 2 - 150, 10),
            color=(0.7, 0.7, 0.7, 1),
            font_size='14sp'
        )
        self.add_widget(self.info_label)

    def reset_game(self):
        """重置游戏状态"""
        # 蛇的初始位置（屏幕中央）
        start_x = self.board_width // 2
        start_y = self.board_height // 2
        self.snake = [(start_x, start_y)]

        self.food = self.new_food()
        self.direction = (1, 0)  # 初始向右移动
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        self.speed = 6  # 初始速度

        # 触摸控制变量
        self.touch_start_pos = None

    def load_high_score(self):
        """加载最高分（简化版本，实际可以存储到文件）"""
        return getattr(self, '_high_score', 0)

    def save_high_score(self):
        """保存最高分"""
        self._high_score = max(self.score, getattr(self, '_high_score', 0))

    def new_food(self):
        """生成新的食物位置"""
        while True:
            food_pos = (
                random.randint(1, self.board_width - 2),
                random.randint(1, self.board_height - 2)
            )
            if food_pos not in self.snake:
                return food_pos

    def on_keyboard_down(self, window, keycode, *args):
        """处理键盘输入"""
        if self.game_over or self.paused:
            return

        # 方向控制
        if keycode == 273 and self.direction != (0, -1):  # 上
            self.direction = (0, 1)
        elif keycode == 274 and self.direction != (0, 1):  # 下
            self.direction = (0, -1)
        elif keycode == 276 and self.direction != (1, 0):  # 左
            self.direction = (-1, 0)
        elif keycode == 275 and self.direction != (-1, 0):  # 右
            self.direction = (1, 0)

    def on_touch_down(self, touch):
        """处理触摸输入"""
        # 检查是否点击了按钮
        if self.pause_btn.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if self.game_over:
            self.restart_game()
            return True

        if self.paused:
            return True

        self.touch_start_pos = touch.pos
        return True

    def on_touch_up(self, touch):
        """处理触摸结束"""
        if self.touch_start_pos is None or self.game_over or self.paused:
            return super().on_touch_up(touch)

        # 计算滑动方向
        dx = touch.pos[0] - self.touch_start_pos[0]
        dy = touch.pos[1] - self.touch_start_pos[1]

        # 最小滑动距离
        min_swipe = 30

        if abs(dx) > abs(dy) and abs(dx) > min_swipe:
            # 水平滑动
            if dx > 0 and self.direction != (-1, 0):  # 右滑
                self.direction = (1, 0)
            elif dx < 0 and self.direction != (1, 0):  # 左滑
                self.direction = (-1, 0)
        elif abs(dy) > min_swipe:
            # 垂直滑动
            if dy > 0 and self.direction != (0, -1):  # 上滑
                self.direction = (0, 1)
            elif dy < 0 and self.direction != (0, 1):  # 下滑
                self.direction = (0, -1)

        self.touch_start_pos = None
        return True

    def start_game(self):
        """开始游戏"""
        if self.game_clock:
            self.game_clock.cancel()
        self.game_clock = Clock.schedule_interval(self.update, 1.0 / self.speed)

    def toggle_pause(self, button):
        """暂停/继续游戏"""
        if self.game_over:
            return

        self.paused = not self.paused
        if self.paused:
            if self.game_clock:
                self.game_clock.cancel()
            button.text = '继续'
        else:
            self.start_game()
            button.text = '暂停'

    def update(self, dt):
        """游戏更新函数"""
        if self.game_over or self.paused:
            return

        # 移动蛇头
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # 检查边界碰撞
        if (new_head[0] < 0 or new_head[0] >= self.board_width or
                new_head[1] < 0 or new_head[1] >= self.board_height):
            self.end_game()
            return

        # 检查自身碰撞
        if new_head in self.snake:
            self.end_game()
            return

        # 添加新的蛇头
        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.new_food()

            # 增加速度
            if self.score % 50 == 0 and self.speed < 15:
                self.speed += 1
                if self.game_clock:
                    self.game_clock.cancel()
                self.start_game()

            # 更新分数显示
            self.score_label.text = f'分数: {self.score}'

            # 更新最高分
            if self.score > self.high_score:
                self.high_score = self.score
                self.high_score_label.text = f'最高分: {self.high_score}'
        else:
            # 如果没吃到食物，删除蛇尾
            self.snake.pop()

        # 重新绘制
        self.draw_game()

    def end_game(self):
        """游戏结束"""
        self.game_over = True
        self.save_high_score()
        if self.game_clock:
            self.game_clock.cancel()

        # 显示游戏结束弹窗
        self.show_game_over_popup()

    def show_game_over_popup(self):
        """显示游戏结束弹窗"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # 游戏结束标题
        title = Label(
            text='游戏结束!',
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        content.add_widget(title)

        # 分数显示
        score_text = Label(
            text=f'本次分数: {self.score}\n最高分: {self.high_score}',
            font_size='18sp',
            size_hint_y=None,
            height=80,
            halign='center'
        )
        content.add_widget(score_text)

        # 按钮布局
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)

        restart_btn = Button(text='重新开始', size_hint_x=0.5)
        restart_btn.bind(on_press=lambda x: (popup.dismiss(), self.restart_game()))
        btn_layout.add_widget(restart_btn)

        content.add_widget(btn_layout)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        popup.open()

    def restart_game(self):
        """重新开始游戏"""
        self.reset_game()
        self.score_label.text = f'分数: {self.score}'
        self.high_score_label.text = f'最高分: {self.high_score}'
        self.pause_btn.text = '暂停'
        self.start_game()
        self.draw_game()

    def draw_game(self):
        """绘制游戏画面"""
        self.canvas.clear()

        with self.canvas:
            # 绘制背景
            Color(0.05, 0.05, 0.1, 1)  # 深蓝色背景
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # 绘制网格线
            Color(0.2, 0.2, 0.3, 0.3)
            for x in range(0, int(Window.width), self.cell_size):
                Line(points=[x, 0, x, Window.height], width=1)
            for y in range(0, int(Window.height), self.cell_size):
                Line(points=[0, y, Window.width, y], width=1)

            # 绘制蛇头（特殊颜色）
            if self.snake:
                Color(0.2, 0.8, 0.2, 1)  # 亮绿色蛇头
                head = self.snake[0]
                Rectangle(
                    pos=(head[0] * self.cell_size + 1, head[1] * self.cell_size + 1),
                    size=(self.cell_size - 2, self.cell_size - 2)
                )

                # 绘制蛇身
                Color(0.1, 0.6, 0.1, 1)  # 深绿色蛇身
                for segment in self.snake[1:]:
                    Rectangle(
                        pos=(segment[0] * self.cell_size + 1, segment[1] * self.cell_size + 1),
                        size=(self.cell_size - 2, self.cell_size - 2)
                    )

            # 绘制食物（带动画效果）
            Color(1, 0.3, 0.3, 1)  # 红色食物
            food_size = self.cell_size - 4
            Rectangle(
                pos=(self.food[0] * self.cell_size + 2, self.food[1] * self.cell_size + 2),
                size=(food_size, food_size)
            )

            # 绘制边界
            Color(0.8, 0.8, 0.8, 1)
            Line(rectangle=(0, 0, Window.width, Window.height), width=2)


class SnakeApp(App):
    def build(self):
        self.title = '贪吃蛇游戏'
        game = SnakeGame()
        return game


if __name__ == '__main__':
    SnakeApp().run()