class Terrain:
    """지형 오브젝트 목록을 보관하는 컨테이너."""
    def __init__(self):
        self.platforms = []
        self.ground_segments = []
        self.spikes = []
        self.ladders = []
        self.decorations = []
        self.enemies = []
        self.world_end = 0
