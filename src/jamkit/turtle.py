import turtle, random
from importlib import resources as importlib_resources
from .sprites import Sprite

def _asset_path(name: str) -> str:
    # Fallback helper raw filenames are passed
    return str(importlib_resources.files("jamkit.assets").joinpath(name))

# Screen / Grid
class Grid:
    def __init__(self, cell=20, width=20, height=20, title="Jam Grid", bg="black"):
        self.cell = cell
        self.W, self.H = width, height
        self.cols, self.rows = width // cell, height // cell

        self.screen = turtle.Screen()
        self.screen.setup(width, height)
        self.screen.title(title)
        self.screen.bgcolor(bg)
        self.screen.tracer(0)

        self.pen = turtle.Turtle(visible=False)
        self.pen.penup()
        self.hud = turtle.Turtle(visible=False)
        self.hud.penup()
        self.hud.color("yellow")
        self.hud.goto(-self.W//2+10, self.H/2-10)

        self._loop_running = False
    
    def to_xy(self, gx, gy):
        x = -self.W//2 + gx*self.cell
        y = -self.H//2 + gy*self.cell
        return x, y

    def draw_cell(self, gx, gy, color):
        self.pen.goto(*self.to_xy(gx, gy))
        self.pen.color(color)
        self.pen.begin_fill()
        for _ in range(4):
            self.pen.forward(self.cell)
            self.pen.left(90)
        self.pen.end_fill()

    def random_cell(self):
        return random.randrange(self.cols), random.randrange(self.rows)

    def clear(self):
        self.pen.clear()

    def write_hud(self, text):
        self.hud.clear()
        self.hud.goto(-self.W//2+10, self.H//2-30)
        self.hud.write(text, font=("Arial", 14, "bold"))

    def message(self, text, color="white", y=0, size=18):
        self.hud.goto(0, y)
        self.hud.color(color)
        self.hud.write(text, align="center", font=("Arial", size, "bold"))
        self.hud.color("yellow")  # reset

    def update(self):
        self.screen.update()

    def loop(self, fn, ms=120):
        # call fn() every ms
        if not self._loop_running:
            self._loop_running = True

        def step():
            if self._loop_running:
                fn()
                self.screen.ontimer(step, ms)
        step()
    
    def run(self):
        # Block and keep the Turtle window open
        turtle.mainloop()

    def stop(self):
        self._loop_running = False

# ---------- Sprites ----------
class Head:
    def __init__(self, grid: Grid, color="lime"):
        self.g = grid
        self.x, self.y = grid.cols // 2, grid.rows // 2
        self.dx, self.dy = 1, 0
        self.color = color

    def move(self, wrap=True):
        self.x += self.dx
        self.y += self.dy
        if wrap:
            self.x %= self.g.cols
            self.y %= self.g.rows

    def draw(self):
        self.g.draw_cell(self.x, self.y, self.color)

    def bind_arrows(self):
        s = self.g.screen
        def up():    self.dx, self.dy = 0,  1
        def down():  self.dx, self.dy = 0, -1
        def left():  self.dx, self.dy = -1, 0
        def right(): self.dx, self.dy = 1,  0
        s.onkey(up, "Up")
        s.onkey(down, "Down")
        s.onkey(left, "Left")
        s.onkey(right, "Right")
        s.listen()
    
    def centre(self, grid: Grid):
        self.x, self.y, self.dx, self.dy = grid.cols//2, grid.rows//2, 1, 0

class Item:
    def __init__(self, grid: Grid, color="red"):
        self.g = grid
        self.color = color
        self.x, self.y = grid.random_cell()

    def place(self, avoid=set()):
        # keep rolling until its not on a forbidden cell
        while True:
            self.x, self.y = self.g.random_cell()
            if (self.x, self.y) not in avoid:
                return

    def draw(self):
        self.g.draw_cell(self.x, self.y, self.color)

# ---------- Tail helper ----------
def draw_tail(grid: Grid, segments, color="green"):
    for sx, sy in segments:
        grid.draw_cell(sx, sy, color)

# ---------- Collision ----------
def hits(a, b):
    return a.x == b.x and a.y == b.y


class ImageItem(Item):
    def __init__(self, grid: Grid, sprite: Sprite | str, fallback_color="orange"):
        super().__init__(grid, color=fallback_color)
        self.g = grid
        self.sprite = sprite
        self.fallback_color = fallback_color

        if isinstance(sprite, Sprite):
            self._shape_path = sprite.path()
        else:
            self._shape_path = _asset_path(str(sprite))

        # One turtle per sprite
        self._t = turtle.Turtle(visible=False)
        self._t.penup()

        try:
            self.g.screen.addshape(self._shape_path)
            self._t.shape(self._shape_path)
            self._t.showturtle()
            self._use_image = True
        except turtle.TurtleGraphicsError:
            self._use_image = False
            self._t.hideturtle()  # fall back to square

    def draw(self):
        if self._use_image:
            x, y = self.g.to_xy(self.x, self.y)
            # centre sprite in cell
            self._t.goto(x + self.g.cell / 2, y + self.g.cell / 2)
        else:
            # fallback to normal cell drawing
            super().draw()