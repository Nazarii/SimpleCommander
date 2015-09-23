#!/usr/bin/env python3

import time
from random import randint

'''
In this game we have two role - invader and hero. Both can bullet.

Invaders are located at the top of game field and always move from the right side to the left and revert.
Also they slowly move to the bottom.

Main hero is located at the centre at the bottom. He can move to the left and to the right.
If he bullet some invader, his bonus is grow.
When invader bullet to main hero, the main hero's life is decrease.
'''

IMAGE_FILENAME = {'background': 'images/bg.png',
                  'hero': 'images/hero.png',
                  'bullet_hero': 'images/bullet_hero',
                  'bullet_invader': 'images/bullet_invader',
                  'invader': ['images/invader1.png', 'images/invader2.png']
                  }


class Unit(object):

    def __init__(self, x, y, bonus, speed, unit_filename, bullet_filename):
        self.image_filename = unit_filename
        self.x = x
        self.y = y
        self.width = 10  # temporary when we don't have real images
        self.height = 10  # must be height of real image
        self.bonus = bonus
        self.speed = speed
        self.is_dead = False
        self.bullet = Bullet(self, bullet_filename)
        self.shift = 5

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def check_fire(self, unit, game_field_height):
        # check if coordinate the bullet and the unit's is the same
        # for this check we also include width and height of invader image
        # (unit.x - unit.width / 2 < bullet.x < unit.x + unit.width / 2)
        # (unit.y - unit.height / 2 < bullet.y < unit.y + unit.height / 2)
        if (self.bullet.x > unit.x - unit.width / 2) and (self.bullet.x < unit.x + unit.width / 2) and \
                (self.bullet.y > unit.y - unit.height / 2) and (self.bullet.y < unit.y + unit.height / 2):
            self.fire(unit)
            return True
        elif self.bullet.y < 0 or self.bullet.y > game_field_height:
            return True
        else:
            return False

    def fire(self, other_unit):
        raise NotImplementedError

    def move_bullet(self):
        raise NotImplementedError


class Invader(Unit):
    moving_speed = 0

    def __init__(self, x, y, bonus=0, speed=5, unit_filename='',
                 bullet_filename=IMAGE_FILENAME.get('bullet_invader', '')):
        if not unit_filename and len(IMAGE_FILENAME.get('invader', [])):
            random_number = randint(0, len(IMAGE_FILENAME.get('invader', [])) - 1)
            unit_filename = IMAGE_FILENAME.get('invader', [])[random_number]
        super(Invader, self).__init__(x, y, bonus, speed, unit_filename, bullet_filename)
        self.moving_speed = speed

    def check_if_move_y(self):
        return self.x <= self.shift

    def set_speed(self, game_field_width):
        # this check for first Invader
        if self.x <= self.shift:
            self.moving_speed = self.speed or -self.speed  # positive value
        # this check for last Invader
        if self.x >= game_field_width:
            self.moving_speed = self.speed < 0 and self.speed or -self.speed  # negative value

    def fire(self, hero):
        if hero.life_count > 1:
            hero.life_count -= 1
        else:
            hero.life_count = 0
            hero.is_dead = True

    def move_bullet(self):
        # Invaders will be at the top and must bullet at the bottom
        # so speed must be positive value
        self.bullet.move(self.speed or -self.speed)


class Hero(Unit):

    def __init__(self, x, y, bonus=0, speed=5, life_count=3, unit_filename=IMAGE_FILENAME.get('hero', ''),
                 bullet_filename=IMAGE_FILENAME.get('bullet_hero', '')):
        super(Hero, self).__init__(x, y, bonus, speed, unit_filename, bullet_filename)
        self.life_count = life_count

    def fire(self, invader):
        self.bonus += invader.bonus
        invader.is_dead = True

    def move_bullet(self):
        # hero will be at the bottom and must bullet at the top
        # so speed must be negative value
        self.bullet.move(-self.speed)


class Bullet():
    def __init__(self, unit, image_filename):
        self.x = unit.x
        self.y = unit.y
        self.image_filename = image_filename

    def move(self, moving_speed):
        self.y += moving_speed


class GameController(object):

    def __init__(self, height, width, invaders_count):
        self.game_field = {'image_filename': IMAGE_FILENAME.get('background', ''), 'height': height, 'width': width}
        self.hero = Hero(self.game_field['height'] / 2, self.game_field['width'] - 10)
        self.invaders_count = invaders_count
        self.Invaders = []
        self.set_invaders()

    def set_invaders(self):
        x = 1
        y = 1
        for count in range(self.invaders_count):
            if self.hero.shift * x >= self.game_field['width']:
                x = 1
                y += 1
            pos_x = self.hero.shift * x
            pos_y = self.hero.shift * y
            self.Invaders.append(Invader(pos_x, pos_y, 10))
            x += 1

    def get_action(self, action, unit_number=0):
        if action == 'bullet_invader':
            move_bullet = True
            while move_bullet:
                self.Invaders[unit_number].move_bullet()
                if self.Invaders[unit_number].check_fire(self.hero, self.game_field['height']):
                    move_bullet = False
                    self.Invaders[unit_number].bullet = Bullet(self.Invaders[unit_number], self.Invaders[unit_number].bullet.image_filename)
        if action == 'bullet_hero':
            move_bullet = True
            while move_bullet:
                self.hero.move_bullet()
                # print 'bullet - ', game_object.hero.bullet.__dict__
                for _invader in self.Invaders:
                    if self.hero.check_fire(_invader, self.game_field['height']):
                        move_bullet = False
                        self.hero.bullet = Bullet(self.hero, self.hero.bullet.image_filename)
        if action == 'move_right':
            self.hero.move_to(self.hero.x + self.hero.speed, self.hero.y)
        if action == 'move_left':
            self.hero.move_to(self.hero.x - self.hero.speed, self.hero.y)

    def run(self):
        game_object = GameController(50, 50, 2)

        '''this code for moving invaders. Work as a job.
            We set moving_speed for positive - if reach the left coordinate of our game field
            or negative  - if we reach the right coordinate of our game field '''

        while not game_object.hero.is_dead and len(game_object.Invaders):
            game_object.Invaders[0].set_speed(game_object.game_field['width'])
            game_object.Invaders[-1].set_speed(game_object.game_field['width'])
            check_if_move_y = game_object.Invaders[0].check_if_move_y()
            random_number = randint(0, len(game_object.Invaders) - 1)
            game_object.get_action('bullet_invader', random_number)
            for invader in game_object.Invaders:
                new_x = invader.x + invader.moving_speed
                new_y = check_if_move_y and invader.y + invader.speed or invader.y
                invader.move_to(new_x, new_y)

            # for invader in game_object.Invaders:
            #     print invader.__dict__

            time.sleep(3)

if __name__ == "__main__":

    '''This example of calling actions such as 'bullet', 'move_left' for our hero
       Also we can call action 'move_right' '''

    # game_object = GameController(50, 50, 2)
    # game_object.get_action('bullet')
    # game_object.get_action('move_left')
    # game_object.get_action('move_left')

    # for invader in game_object.Invaders:
    #     print 'invader - ', invader.__dict__
    # print 'hero - ', game_object.hero.__dict__
