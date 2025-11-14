# pi_eater.py — using jamkit.py
from jamkit.turtle import Grid, Head, ImageItem, Item, draw_tail, hits
from jamkit import sprites

# 32 x 40, 30
g = Grid(cell=32, width=1280, height=960, title="Pi Eater", bg="black")
head = Head(g, color="lime")
head.bind_arrows()

raspberry = ImageItem(g, sprites.raspberry)
pi_bad = Item(g, color="red")

score = 0
tail = [] # list of (x,y)
grow = 0
game_over = False

def step():
    global score, grow, game_over

    if game_over:
        return

    # move & tail follow
    head.move(wrap=True)
    tail.insert(0, (head.x, head.y))
    if grow > 0:
        grow -= 1
    else:
        if tail: tail.pop()

    # if eat raspberry
    if hits(head, raspberry):
        score += 1
        grow += 2
        # avoid tail spawn
        raspberry.place(avoid=set(tail + [(head.x, head.y)]))

    # if hit bug
    if hits(head, pi_bad):
        game_over = True
        g.message("GAME OVER — press R to restart", y=0, color="white")
        g.update()
        return

    # draw
    g.clear()
    raspberry.draw()
    pi_bad.draw()
    draw_tail(g, tail, color="green")
    head.draw()
    g.write_hud(f"Score: {score}")
    g.update()

def reset():
    global score, grow, game_over, tail
    score, grow, game_over = 0, 0, False
    tail.clear()
    head.x, head.y, head.dx, head.dy = g.cols//2, g.rows//2, 1, 0
    raspberry.place()
    pi_bad.place()
    g.clear()
    g.write_hud(f"Score: {score}")
    g.update()

g.screen = g.screen  # access for keys
g.screen.onkey(reset, "r")
g.screen.listen()

# initial place & go
reset()
g.loop(step, ms=120)
g.run()