# Adventures of Mac McMill
# 5/22/19
__author__ = 'Ben Browner'

try:
    from pyglet.gl import *
    from pyglet import *
    from pyglet.window import *
    import random as r
    import math as m
    import time
    import sys
except:
    print('look ma, I used try except!')
    print('You messed up your imports')
    sys.exit()


class Rect:
    # Rect class makes and draws OpenGl rectangles based on __init__ params
    def __init__(self, x, y, w, h, isPlayer=False):
        # init x and y coord (bottom left) and with and height
        self.set(x, y, w, h)
        self.isPlayer = isPlayer
        self.coords = [self._x, self._y, self._w, self._h]

    def draw(self, moveX=None, moveY=None):
        # overides Pyglet's draw method and draws it through openGl GL_QUADS
        # draw method is self referencing since it needs output from self.set()
        if self.isPlayer:
            self._color = ('c3B', (
            0, 0, 255, #BOTTOM-LEFT
            0, 255, 0, #BOTTOM-RIGHT
            255, 0, 0, #UP-RIGHT
            255, 255, 255  #UP-LEFT
            ))
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self._quad, self._color)
            if moveX != None or moveY != None:
                glLineWidth(3)
                pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                     ('v2f', (self._x, self._y, self._x, self._y + moveY)),
                                     ('c3f', (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)))
                pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                     ('v2f', (self._x, self._y, self._x  + moveX, self._y)),
                                     ('c3f', (0.0, 1.0, 0.0, 0.0, 1.0, 0.0)))
        else:
            self._color = ('c3B', (
            210, 210, 210, #BOTTOM-LEFT
            210, 210, 210, #BOTTOM-RIGHT
            255, 255, 255, #UP-RIGHT
            255, 255, 255  #UP-LEFT
            ))
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self._quad, self._color)
            # glLineWidth(3)
            # pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
            #                      ('v2f', (self._x,self._y,self._x + self._w, self._y + self._h)),
            #                      ('c3f', (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)))
            # pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
            #                      ('v2f', (self._x, self._y + self._h,self._x + self._w, self._y)),
            #                      ('c3f', (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)))
    def set(self, x=None, y=None, w=None, h=None):
        # Initializes the vaulues for the draw method
        # Returns via repr (which turns object instance to a strict string)
        self._x = self._x if x is None else x
        self._y = self._y if y is None else y
        self._w = self._w if w is None else w
        self._h = self._h if h is None else h

        self._quad = ('v2f', (self._x, self._y,
                              self._x + self._w, self._y,
                              self._x + self._w, self._y + self._h,
                              self._x, self._y + self._h))
        self.coords = [self._x, self._y, self._w, self._h]

    def __repr__(self):
        # see set method
        return f"Rect(x= {self._x} , y= {self._y} , w= {self._w} , h= {self._h} , isPlayer= {self.isPlayer} )"

class MyWindow(pyglet.window.Window):
    # MyWindow references the pyglet.window.Window object
    # Does the caulcualtion and drawing, basiclly the entire engine
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rec = []
        # List or rectangles to draw
        self.WhichWay = 0
        self.speed = 5
        # Speed multiplication on y and x movements
        self.rand_spawn_blocks = 30
        # Amount of rectangles to draw on draw
        self.gravity = 0.7 # 0.6
        # How fast the apple falls
        self.moveX = 0
        self.moveY = 0
        # X and Y movement vectors

        self.contact_side = 0

        self.isFlying = False
        self.isFalling = True
        # Booleans for checking sates

        self.old_side = 0
        self.contact_side = 0
        self.col = False

        self.max_speed = 50 #25
        self.moving = True


        # self.dimon = pyglet.media.StaticSource(pyglet.media.load('dimon2.wav'))


    def draw_rectangles(self):
        # Creates a batch of rectangle coords that will be drawn later
        self.clear()

        self.recs = []
        self.recs.append(Rect(-100, -40, 1380, 80))
        for i in range(1, self.rand_spawn_blocks):
            self.recs.append(Rect(r.randint(1, 1280), r.randint(1, 720), r.randint(5, 100), r.randint(5, 100)))

    def player_draw(self):
        # draw the player on run
        self.player = Rect(50, 50, 15, 30, True)

    def isDigit(self, n):
        # allow isdigit to return negatives
        return n.strip('-').isdigit()

    def collison(self, x, y, w, h):
        # Returns a boolean when player is intersecting a rectangle
        self.px = x
        self.py = y
        self.opx = w
        self.opy = h
        for platform in self.recs:
            self.rect_coord = [int(s) for s in str(platform).split() if self.isDigit(s)]
            self.bx = self.rect_coord[0]
            self.by = self.rect_coord[1]
            self.obx = self.rect_coord[2]
            self.oby = self.rect_coord[3]
            if self.py <= self.by + self.oby and self.py >= self.by - self.opy:
                if self.px <= self.bx + self.obx and self.px >= self.bx - self.opx:
                    return True
        return False

    def p_col_dir(self):
        # Figure out which side player intersected if collison is True
        # Uses the diagnols of a rectangle to digure this out
        self.px = self.player.coords[0]
        self.py = self.player.coords[1] - self.moveY
        self.opx = self.player.coords[2] + self.px
        self.opy = self.player.coords[3] + self.py
        self.bx = self.rect_coord[0]
        self.by = self.rect_coord[1]
        self.obx = self.rect_coord[2] + self.bx
        self.oby = self.rect_coord[3] + self.by

        #      +--------------------------+
        #      |            1             |
        #      |            |             |
        #      | 4----------+-----------2 |
        #      |            |             |
        #      |            3             |
        #      +--------------------------+

        self.pos_slope = (self.by - self.oby) / (self.bx - self.obx)
        self.neg_slope = -self.pos_slope


        self.center_x = self.bx + ((self.obx - self.bx) / 2)
        self.center_y = self.by + ((self.oby - self.by) / 2)



        self.g_pos_slope = self.py - self.center_y > self.pos_slope * (self.px - self.center_x)
        # self.l_pos_slope = self.py - self.center_y < self.pos_slope * (self.px - self.center_x)
        self.g_neg_slope = self.py - self.center_y > self.neg_slope * (self.px - self.center_x)
        # self.l_neg_slope = self.py - self.center_y < self.neg_slope * (self.px - self.center_x)

        #todo compensate over shooting sectors because of gravity. X and Y movements need to be checked
        #todo done

        if self.col:
            if self.g_pos_slope and self.g_neg_slope:
                self.contact_side = 1
            elif not self.g_pos_slope and self.g_neg_slope:
                self.contact_side = 2
            elif not self.g_pos_slope and not self.g_neg_slope:
                self.contact_side = 3
            elif self.g_pos_slope and not self.g_neg_slope:
                self.contact_side = 4
        else:
            self.contact_side = 0


    def move(self):
        # Handles all things related to moving the player
        self.col = self.collison(self.player.coords[0], self.player.coords[1], self.player.coords[2], self.player.coords[3])
        self.p_col_dir()

        if self.moveY != 0:
            self.isFalling = True

        if self.moveY > self.max_speed:
            self.moveY = self.max_speed
        elif self.moveY < -self.max_speed:
            self.moveY = -self.max_speed

        if self.contact_side > 0:
            if self.contact_side == 1 and self.isFalling:
                self.moveY = 0
                self.moveX = 0
                self.player.set(self.px, self.oby, 15, 30)
                self.isFalling = False
            elif self.contact_side == 2:
                self.player.set(self.obx + 1, self.py, 15, 30)
                self.moveX = 0
            elif self.contact_side == 3:
                self.player.set(self.px, self.by-self.player.coords[3]-1, 15, 30)
                self.moveY = 0
            elif self.contact_side == 4:
                self.player.set(self.bx-self.player.coords[2]-1, self.py, 15, 30)
                self.moveX = 0
        else:
            self.moveY -= self.gravity

        if not self.moving:
            if self.moveX > 0:
                self.moveX -= self.speed / 10
            elif self.moveX < 0:
                self.moveX += self.speed / 10


    def on_draw(self):
        # pyglet.window method that is called every game tick
        # refreshes the board and draws rectangles from batch and player
        self.clear()
        for i in self.recs:
            i.draw()
        self.player.draw(self.moveX, self.moveY)
        self.player.set(self.player._x + self.moveX, self.player._y + self.moveY, 15, 30)
        if not self.isFlying:
            self.move()
        if self.px < 0 or self.px > self.width or self.py < 0 or self.py > self.height + 1000:
            self.player.set(50, 50, 15, 30)
            self.moveX = 0
            self.moveY = 0
        #todo download comic sans
        self.label = pyglet.text.Label(f'Speed: {str(self.speed)}, C: {self.col}, R: {self.rand_spawn_blocks}, Flying: {self.isFlying}, '
                                       f'Falling: {self.isFalling}, Side: {self.contact_side}, X: {self.player.coords[0]}, Y: {self.player.coords[1]}',
                                  font_name='Comic Sans',
                                  font_size=10,
                                  x=20, y=700,
                                  anchor_x='left', anchor_y='center')

        self.label.color = (155, 155, 155, 255)
        self.label.draw()

    def on_key_press(self, symbol, modifiers):
        # pyglet.window method that runs everytime you press a key
        if self.isFlying:
            if symbol == key.W:
                self.moveY = self.speed
            elif symbol == key.S:
                self.moveY = -self.speed
            elif symbol == key.A:
                self.moveX = -self.speed
            elif symbol == key.D:
                self.moveX = self.speed
        else:
            if (symbol == key.SPACE or symbol == key.W) and not self.isFalling:
                self.moveY = self.speed * 3
                self.isFalling = True
            elif symbol == key.A:
                self.moveX += -self.speed
                self.moving = True
            elif symbol == key.D:
                self.moveX += self.speed
                self.moving = True
        if symbol == key.LEFT:
            self.rand_spawn_blocks -= 1
            self.draw_rectangles()
        elif symbol == key.RIGHT:
            self.rand_spawn_blocks += 1
            self.draw_rectangles()
        elif symbol == key.UP:
            self.speed += 1
        elif symbol == key.DOWN:
            self.speed -= 1
        elif symbol == key.R:
            self.draw_rectangles()
        elif symbol == key.L:
            self.player.set(50, 50, 15, 30)
            self.moveX = 0
            self.moveY = 0
        elif symbol == key.ESCAPE:
            sys.exit('UR_MOM')
        elif symbol == key.V:
            self.isFlying = not self.isFlying

    def on_key_release(self, symbol, modifiers):
        # pyglet.window method that runs everytime you release a key
        if self.isFlying:
            self.moveX = 0
            self.moveY = 0
        else:
            self.moving = False


    def on_close(self):
        # closes the window when you press the red exit button
        sys.exit('UR_MOM')




def main():
    # Main method
    window = MyWindow(1280, 720, "The Adventure of Mac McMill", visible=False)
    icon1 = pyglet.image.load('cory_64x64.png')
    window.set_icon(icon1)
    window.set_visible(True)
    window.activate()

    window.draw_rectangles()
    window.player_draw()

    # Game loop (for some reason this works better than the standard way)
    while True:
        pyglet.clock.tick()

        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')


        window.flip()

# MAIN CALL
if __name__ == '__main__':
    main()