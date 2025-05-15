import pygame
import numpy as np
import pyaudio
import threading
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Tetris pieces
pieces = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

# PyAudio setup for Game Boy Tetris theme (Korobeiniki)
def play_tetris_theme():
    p = pyaudio.PyAudio()
    frequencies = [261.63, 329.63, 392.00, 523.25, 659.26, 784.00, 880.00, 987.77, 1046.50, 1174.66, 1318.51, 1396.91]
    duration = 0.2  
    fs = 44100  
    for freq in frequencies:
        samples = (np.sin(2 * np.pi * np.arange(fs * duration) * freq / fs)).astype(np.float32)
        audio = samples * (2**15 - 1) / np.max(np.abs(samples))
        audio = audio.astype(np.int16)
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=fs,
                        output=True)
        stream.write(audio.tobytes())
        stream.stop_stream()
        stream.close()
    p.terminate()

# Start the Tetris theme in a separate thread
threading.Thread(target=play_tetris_theme).start()

class Tetris:
    def __init__(self):
        self.grid_width = 10
        self.grid_height = 20
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.piece_types = list(pieces.keys())
        self.current_piece = self.get_random_piece()
        self.piece_x = self.grid_width // 2
        self.piece_y = 0
        self.score = 0
        self.level = 0
        self.lines_cleared = 0
        self.drop_speed = 30  # Lower is faster

    def get_random_piece(self):
        piece_type = random.choice(self.piece_types)
        return {'type': piece_type, 'shape': pieces[piece_type], 'rotation': 0}

    def rotate_piece(self):
        self.current_piece['rotation'] = (self.current_piece['rotation'] + 1) % 4

    def get_piece_shape(self):
        shape = self.current_piece['shape']
        rotation = self.current_piece['rotation']
        for _ in range(rotation):
            shape = list(zip(*shape[::-1]))
        return shape

    def check_collision(self, x, y):
        shape = self.get_piece_shape()
        for i, row in enumerate(shape):
            for j, val in enumerate(row):
                if val and (x + j < 0 or x + j >= self.grid_width or y + i >= self.grid_height or self.grid[y + i][x + j]):
                    return True
        return False

    def clear_lines(self):
        lines_to_clear = []
        for i, row in enumerate(self.grid):
            if all(row):
                lines_to_clear.append(i)
        for line in sorted(lines_to_clear, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(self.grid_width)])
        self.lines_cleared += len(lines_to_clear)
        if len(lines_to_clear) == 1:
            self.score += 100
        elif len(lines_to_clear) == 2:
            self.score += 300
        elif len(lines_to_clear) == 3:
            self.score += 500
        elif len(lines_to_clear) == 4:
            self.score += 800
        self.level = self.lines_cleared // 10

    def update(self):
        if self.check_collision(self.piece_x, self.piece_y + 1):
            shape = self.get_piece_shape()
            for i, row in enumerate(shape):
                for j, val in enumerate(row):
                    if val:
                        self.grid[self.piece_y + i][self.piece_x + j] = 1
            self.clear_lines()
            self.current_piece = self.get_random_piece()
            self.piece_x = self.grid_width // 2
            self.piece_y = 0
        else:
            self.piece_y += 1

    def draw(self):
        screen.fill(BLACK)
        grid_x = (SCREEN_WIDTH - self.grid_width * 20) // 2
        grid_y = (SCREEN_HEIGHT - self.grid_height * 20) // 2
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(screen, WHITE, (x * 20 + grid_x, y * 20 + grid_y, 20, 20))
        shape = self.get_piece_shape()
        for i, row in enumerate(shape):
            for j, val in enumerate(row):
                if val:
                    pygame.draw.rect(screen, RED, ((self.piece_x + j) * 20 + grid_x, (self.piece_y + i) * 20 + grid_y, 20, 20))
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(text, (10, 10))
        text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(text, (10, 50))
        pygame.display.flip()

# Main game loop
tetris = Tetris()
running = True
last_update = pygame.time.get_ticks()
move_left = False
move_right = False
move_down = False
update_interval = 1000 // 60  # Update at 60 Hz (NTSC-like frame rate)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            elif event.key == pygame.K_d:
                move_right = True
            elif event.key == pygame.K_s:
                move_down = True
            elif event.key == pygame.K_w:
                tetris.rotate_piece()
                if tetris.check_collision(tetris.piece_x, tetris.piece_y):
                    tetris.rotate_piece()
                    tetris.rotate_piece()
                    tetris.rotate_piece()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            elif event.key == pygame.K_d:
                move_right = False
            elif event.key == pygame.K_s:
                move_down = False

    current_time = pygame.time.get_ticks()
    if current_time - last_update >= update_interval:
        if move_left:
            if not tetris.check_collision(tetris.piece_x - 1, tetris.piece_y):
                tetris.piece_x -= 1
        if move_right:
            if not tetris.check_collision(tetris.piece_x + 1, tetris.piece_y):
                tetris.piece_x += 1
        if move_down:
            tetris.update()
        else:
            drop_counter = current_time - last_update
            if drop_counter >= tetris.drop_speed - tetris.level * 2:
                tetris.update()
        last_update = current_time

    tetris.draw()
    clock.tick(60)

pygame.quit()
