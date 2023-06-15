from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, \
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window


class PongPaddle(Widget):
    score = NumericProperty(0)

    MOVE_STOP = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    SPEED = 10
    move_direction = MOVE_STOP

    up_key = None
    down_key = None
    def set_input_keys(self, up_key, down_key):
        self.up_key = up_key
        self.down_key = down_key

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == self.up_key:
            self.move_direction = PongPaddle.MOVE_UP
        elif keycode[1] == self.down_key:
            self.move_direction = PongPaddle.MOVE_DOWN
        return True
    def on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == self.up_key:
            self.move_direction = PongPaddle.MOVE_STOP
        elif keycode[1] == self.down_key:
            self.move_direction = PongPaddle.MOVE_STOP
        return True
    def move(self, game):
        if self.move_direction == PongPaddle.MOVE_UP:
            if game.top > self.top:
                self.center_y += PongPaddle.SPEED
        if self.move_direction == PongPaddle.MOVE_DOWN:
            if game.y < self.y:
                self.center_y -= PongPaddle.SPEED

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.05
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos



class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.player1.set_input_keys('w', 's')
        self.player2.set_input_keys('up', 'down')
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)

        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

    def _keyboard_closed(self):
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self._keyboard = None
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.player2.on_keyboard_down(keyboard, keycode, text, modifiers)
        self.player1.on_keyboard_down(keyboard, keycode, text, modifiers)

    def _on_key_up(self, keyboard, keycode):
        self.player1.on_keyboard_up(keyboard, keycode)
        self.player2.on_keyboard_up(keyboard, keycode)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()
        self.player1.move(self)
        self.player2.move(self)
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))
        if self.player1.score >= 10 or self.player2.score >= 10:

            self.player1.score = 0
            self.player2.score = 0
    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':

    PongApp().run()
