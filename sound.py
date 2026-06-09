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

    def play(self, sfx: SoundEffect, loops: int = 0) -> mixer.Sound | None:
        if sfx in self.sounds:
            sound = self.sounds[sfx]
            sound.play(loops=loops)
            return sound
