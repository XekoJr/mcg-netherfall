import pygame

class MusicManager:
    def __init__(self):
        self.game_music = pygame.mixer.Sound('./assets/audio/ingame-music.wav')
        self.boss_music = pygame.mixer.Sound('./assets/audio/boss-music.wav')
        self.game_music.set_volume(0.1)
        self.boss_music.set_volume(0.1)

    def play_game_music(self):
        self.boss_music.stop()  # Stop boss music
        self.game_music.play(-1)  # Loop regular game music

    def play_boss_music(self):
        self.game_music.stop()  # Stop regular game music
        self.boss_music.play(-1)  # Loop boss music
