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

        for sound in self.sounds.values():
            sound.set_volume(0.75)

    def play(self, sfx: SoundEffect):
        if sfx in self.sounds:
            self.sounds[sfx].play()
