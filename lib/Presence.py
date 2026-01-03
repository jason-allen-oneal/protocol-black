# Presence.py
class PresenceSystem:
    def __init__(self):
        self.level = 0.0

    def update(self, dt, player):
        self.level += dt * 0.5
        self.level = min(self.level, 100.0)

    def is_dangerous(self):
        return self.level > 70.0
