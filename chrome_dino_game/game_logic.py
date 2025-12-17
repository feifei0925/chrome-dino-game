import time
import random
from enum import Enum

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"

class DinoGame:
    def __init__(self, player_name="Player"):
        self.state = GameState.MENU
        self.player_name = player_name
        self.score = 0
        self.high_score = 0
        self.speed = 5
        self.game_start_time = 0
        
        self.dino = {
            'x': 50,
            'y': 150,
            'width': 40,
            'height': 60,
            'is_jumping': False,
            'y_velocity': 0,
            'is_ducking': False
        }
        self.obstacles = []
        self.clouds = []
        self.ground_offset = 0
        
    def start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.speed = 5
        self.obstacles = []
        self.clouds = []
        self.game_start_time = time.time()
        
        self.dino['y'] = 150
        self.dino['is_jumping'] = False
        self.dino['y_velocity'] = 0
        self.dino['is_ducking'] = False
        
    def update(self):
        if self.state != GameState.PLAYING:
            return
            
        self.score += 1
        if self.score % 100 == 0:
            self.speed += 0.5
        
        if self.dino['is_jumping']:
            self.dino['y'] += self.dino['y_velocity']
            self.dino['y_velocity'] += 0.8
            
            if self.dino['y'] >= 150:
                self.dino['y'] = 150
                self.dino['is_jumping'] = False
                self.dino['y_velocity'] = 0
        
        if random.random() < 0.02 and len(self.obstacles) < 3:
            obstacle_type = random.choice(['cactus', 'bird'])
            obstacle = {
                'type': obstacle_type,
                'x': 400,
                'y': 150 if obstacle_type == 'cactus' else 100,
                'width': 30 if obstacle_type == 'cactus' else 40,
                'height': 50 if obstacle_type == 'cactus' else 30
            }
            self.obstacles.append(obstacle)
        
        for obstacle in self.obstacles:
            obstacle['x'] -= self.speed
        
        self.obstacles = [o for o in self.obstacles if o['x'] > -50]
        
        if random.random() < 0.01 and len(self.clouds) < 5:
            cloud = {
                'x': 400,
                'y': random.randint(50, 100),
                'width': 40,
                'height': 20
            }
            self.clouds.append(cloud)
        
        for cloud in self.clouds:
            cloud['x'] -= self.speed * 0.5
        
        self.clouds = [c for c in self.clouds if c['x'] > -50]
        
        self.ground_offset = (self.ground_offset - self.speed) % 1200
        
        if self.check_collision():
            self.state = GameState.GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
    
    def check_collision(self):
        for obstacle in self.obstacles:
            if (self.dino['x'] < obstacle['x'] + obstacle['width'] and
                self.dino['x'] + self.dino['width'] > obstacle['x'] and
                self.dino['y'] < obstacle['y'] + obstacle['height'] and
                self.dino['y'] + self.dino['height'] > obstacle['y']):
                return True
        return False
    
    def jump(self):
        if not self.dino['is_jumping'] and not self.dino['is_ducking']:
            self.dino['is_jumping'] = True
            self.dino['y_velocity'] = -15
            return True
        return False
    
    def duck(self, is_ducking):
        self.dino['is_ducking'] = is_ducking
        if is_ducking:
            self.dino['height'] = 30
            self.dino['y'] = 180
        else:
            self.dino['height'] = 60
            self.dino['y'] = 150
    
    def get_state(self):
        return {
            'state': self.state.value,
            'score': self.score,
            'high_score': self.high_score,
            'speed': self.speed,
            'dino': self.dino.copy(),
            'obstacles': self.obstacles.copy(),
            'clouds': self.clouds.copy(),
            'ground_offset': self.ground_offset
        }