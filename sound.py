from enums import SoundEffect
from pygame import mixer


class SoundManager:
    def __init__(self):
        mixer.init()

        self.sounds = {
            SoundEffect.MOVE: mixer.Sound("sounds/move.wav"),
            SoundEffect.INTERACT: mixer.Sound("sounds/interact.wav"),
            SoundEffect.GAME: mixer.Sound("sounds/game.wav"),
            SoundEffect.END: mixer.Sound("sounds/end.wav"),
        }

        volumes = {
            SoundEffect.MOVE: 0.35,
            SoundEffect.INTERACT: 0.35,
            SoundEffect.GAME: 1,
            SoundEffect.END: 0.75,
        }
        for sound, volume in volumes.items():
            self.sounds[sound].set_volume(volume)

    def play(self, sfx: SoundEffect):
        if sfx in self.sounds:
            self.sounds[sfx].play()
