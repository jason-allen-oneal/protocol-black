# Audio.py
class AudioManager:
    def __init__(self, base):
        self.base = base
        self.ambient = base.loader.loadSfx("assets/sound/music/title.mp3")
        self.ambient.setLoop(True)
        self.ambient.setVolume(0.2)
        self.ambient.play()

    def update(self, dt, presence):
        self.ambient.setVolume(0.5 if presence.is_dangerous() else 0.2)
