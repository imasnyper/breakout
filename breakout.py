import os, sys, time
import pygame
from pygame.locals import *

COLORS = {
    1: "blue",
    2: "green",
    3: "orange",
    4: "purple",
    5: "red",
    6: "yellow"
}

def load_image(name, colorkey=None):
    fullname = os.path.join("assets", "sprites", name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image: ", name)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
    
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join("data", name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print("Cannot load sound: ", fullname)
        raise SystemExit(message)
    return sound

class Paddle(pygame.sprite.Sprite):
    def __init__(self, ball):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("paddle.png")
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.midbottom = self.area.midbottom
        self.rect.bottom -= 12
        self.epoch = time.time()
        self.hitTime = time.time()
        self.ball = ball


    def moveLeft(self):
        if(self.rect.left > self.area.left and time.time() - self.epoch > .01 * .4):
            self.epoch = time.time()
            self.rect.left -= 1

    def moveRight(self):
        if(self.rect.right < self.area.right and time.time() - self.epoch > .005):
            self.epoch = time.time()
            self.rect.right += 1

    def update(self):
        ballYHit = self.ball.rect.bottom > self.rect.top
        ballLeftX = self.ball.rect.right > self.rect.left
        ballRightX = self.ball.rect.left < self.rect.right
        if(ballYHit and ballLeftX and ballRightX and time.time() - self.hitTime > .1):
            self.hitTime = time.time()
            self.ball.invertYDirection()


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("ball.png")
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.center = self.area.center
        self.speed = 1
        self.direction = (-1,-1)
        self.epoch = time.time()
        self.alive = True
    
    def update(self):
        if(time.time() - self.epoch > .01 * .75):
            self.epoch = time.time()
            if(self.rect.right < self.area.right and self.direction[0] > 0 
                or self.rect.left > self.area.left and self.direction[0] < 0):
                self.rect.left += self.direction[0]
            else:
                self.invertXDirection()
            if(self.rect.top > self.area.top and self.direction[1] < 0
                or self.rect.bottom < self.area.bottom and self.direction[1] > 0):
                self.rect.top += self.direction[1]
            elif(self.rect.bottom >= self.area.bottom):
                self.alive = False
            else:
                self.invertYDirection()

    def invertYDirection(self):
        self.direction = (self.direction[0], self.direction[1] * -1)

    def invertXDirection(self):
        self.direction = (self.direction[0] * -1, self.direction[1])


def get_key(val):
    for key, value in COLORS.items():
        if val == value:
            return key

    return "key doesn't exist"

class Brick(pygame.sprite.Sprite):
    def __init__(self, ball, color=COLORS[4], position=(48, 12)):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(color + "_brick.png")
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.topleft = position
        self.color = color
        self.value = get_key(color)
        self.ball = ball
        self.epoch = time.time()
        self.cornerCollisions = []

    def update(self):
        collision = False
        if(self.epoch > .01):
            self.epoch = time.time()
            collisions = getCollidePoints(self.ball.rect, self.rect)
            ballCollisions = getCollidePoints(self.rect, self.ball.rect)

            checkCollisions = [x for x in collisions.values() if x != 0]


            if collisions["topleft"] and collisions["midtop"]:
                self.ball.invertYDirection()
                collision = True
            elif collisions["topright"] and collisions["midtop"]:
                self.ball.invertYDirection()
                collision = True
            elif collisions["topleft"] and collisions["midleft"]:
                self.ball.invertXDirection()
                collision = True
            elif collisions["topright"] and collisions["midright"]:
                self.ball.invertXDirection()
                collision = True
            elif collisions["bottomleft"] and collisions["midleft"]:
                self.ball.invertXDirection()
                collision = True
            elif collisions["bottomright"] and collisions["midright"]:
                self.ball.invertXDirection()
                collision = True
            elif collisions["bottomleft"] and collisions["midbottom"]:
                self.ball.invertYDirection()
                collision = True
            elif collisions["bottomright"] and collisions["midbottom"]:
                self.ball.invertYDirection()
                collision = True
            
            elif collisions["midtop"]:
                self.ball.invertYDirection()
                collision = True
            elif collisions["midbottom"]:
                self.ball.invertYDirection()
                collision = True
            elif collisions["midleft"]:
                self.ball.invertXDirection()
                collision = True
            elif collisions["midright"]:
                self.ball.invertXDirection()
                collision = True

            #corner checks

            elif collisions["topleft"]:
                for collision in [x for x,y in ballCollisions.items() if y]:
                    if collision.find("right") >= 0:
                        self.ball.invertXDirection()
                        collision = True
                        break
                    elif collision.find("bottom") >= 0:
                        self.ball.invertYDirection()
                        collision = True
                        break
            elif collisions["topright"]:
                for collision in [x for x,y in ballCollisions.items() if y]:
                    if collision.find("left") >= 0:
                        self.ball.invertXDirection()
                        collision = True
                        break
                    elif collision.find("bottom") >= 0:
                        self.ball.invertYDirection()
                        collision = True
                        break
            elif collisions["bottomleft"]:
                for collision in [x for x,y in ballCollisions.items() if y]:
                    if collision.find("right") >= 0:
                        self.ball.invertXDirection()
                        collision = True
                        break
                    elif collision.find("top") >= 0:
                        self.ball.invertYDirection()
                        collision = True
                        break
            elif collisions["bottomright"]:
                for collision in [x for x,y in ballCollisions.items() if y]:
                    if collision.find("left") >= 0:
                        self.ball.invertXDirection()
                        collision = True
                        break
                    elif collision.find("bottom") >= 0:
                        self.ball.invertYDirection()
                        collision = True
                        break


            # print("here")

            # ballRectCP = self.ball.rect.collidepoint
            # if(ballRectCP(self.rect.midleft)
            #     or ballRectCP(self.rect.midright)):
            #     self.ball.invertXDirection()
            #     collision = True

            # elif(ballRectCP(self.rect.midtop)
            #     or ballRectCP(self.rect.midbottom)):
            #     self.ball.invertYDirection()
            #     collision = True

            if collision:
                self.kill()
        
        # if(self.rect.colliderect(ball.rect)):
        #     self.ball.invertYDirection()
        #     self.kill()

def getCollidePoints(ballRect, brickRect):
    collisions = {}

    collisions["topleft"] = ballRect.collidepoint(brickRect.topleft)
    collisions["midtop"] = ballRect.collidepoint(brickRect.midtop)
    collisions["topright"] = ballRect.collidepoint(brickRect.topright)
    
    collisions["midleft"] = ballRect.collidepoint(brickRect.midleft)
    collisions["center"] = ballRect.collidepoint(brickRect.center)
    collisions["midright"] = ballRect.collidepoint(brickRect.midright)
    
    collisions["bottomleft"] = ballRect.collidepoint(brickRect.bottomleft)
    collisions["midbottom"] = ballRect.collidepoint(brickRect.midbottom)
    collisions["bottomright"] = ballRect.collidepoint(brickRect.bottomright)

    return collisions

def makeLevelOne(ball):
    bricks = []
    brickColors = list(COLORS.values())
    for y in range(4):
        for x in range(8):
            bricks.append(Brick(ball, brickColors[y], (48*(x+1), 12*(y+4))))

    return bricks

if __name__ == "__main__":
    if not pygame.font: print("Warning, fonts disabled.")
    if not pygame.mixer: print("Warning, sounds disabled.")

    score = 0
    
    pygame.init()
    screen = pygame.display.set_mode((480, 680))
    pygame.display.set_caption("Breakout")
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((43, 43, 43))

    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Breakout", 1, (255, 255, 255))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos)

    screen.blit(background, (0,0))
    pygame.display.flip()

    ball = Ball()
    paddle = Paddle(ball)
    
    levelOneBricks = makeLevelOne(ball)

    allsprites = pygame.sprite.RenderPlain((paddle, ball, *levelOneBricks))
    clock = pygame.time.Clock()

    paddleMovingRight = False
    paddleMovingLeft = False

    running = True
    while running:
        clock.tick()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_LEFT or event.key == K_w:
                    paddleMovingLeft = True
                if event.key == K_RIGHT or event.key == K_d:
                    paddleMovingRight = True

            if event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_w:
                    paddleMovingLeft = False
                if event.key == K_RIGHT or event.key == K_d:
                    paddleMovingRight = False
        
        if paddleMovingLeft:
            paddle.moveLeft()
        if paddleMovingRight:
            paddle.moveRight()

        allsprites.update()                        

        if(not ball.alive):
            running = False

        screen.blit(background, (0,0))
        allsprites.draw(screen)
        pygame.display.flip()