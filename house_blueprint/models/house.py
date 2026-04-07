"""House model."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from .room import Room, RoomType


@dataclass
class House:
    name: str = "My House"
    rooms: List[Room] = field(default_factory=list)
    stories: int = 1
    wall_thickness: float = 0.5
    scale: float = 10.0
    
    def add_room(self, room: Room) -> 'House':
        self.rooms.append(room)
        return self
    
    def get_room(self, name: str) -> Optional[Room]:
        for room in self.rooms:
            if room.name == name:
                return room
        return None
    
    @property
    def total_area(self) -> float:
        return sum(room.area for room in self.rooms)
    
    @property
    def width(self) -> float:
        if not self.rooms:
            return 0.0
        min_x = min(room.x for room in self.rooms)
        max_x = max(room.x + room.width for room in self.rooms)
        return max_x - min_x
    
    @property
    def height(self) -> float:
        if not self.rooms:
            return 0.0
        min_y = min(room.y for room in self.rooms)
        max_y = max(room.y + room.height for room in self.rooms)
        return max_y - min_y
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        if not self.rooms:
            return (0, 0, 0, 0)
        min_x = min(room.x for room in self.rooms)
        min_y = min(room.y for room in self.rooms)
        max_x = max(room.x + room.width for room in self.rooms)
        max_y = max(room.y + room.height for room in self.rooms)
        return (min_x, min_y, max_x, max_y)
    
    def validate_layout(self) -> Tuple[bool, List[str]]:
        errors = []
        for i, room1 in enumerate(self.rooms):
            for room2 in self.rooms[i + 1:]:
                if room1.intersects(room2):
                    errors.append(f"Rooms '{room1.name}' and '{room2.name}' overlap")
        return (len(errors) == 0, errors)
    
    def get_statistics(self) -> Dict:
        room_type_counts = {}
        for room in self.rooms:
            rt = room.room_type.value
            room_type_counts[rt] = room_type_counts.get(rt, 0) + 1
        
        return {
            'total_rooms': len(self.rooms),
            'total_area': self.total_area,
            'dimensions': f"{self.width:.1f}' x {self.height:.1f}'",
            'width': self.width,
            'height': self.height,
            'room_type_counts': room_type_counts,
            'average_room_size': self.total_area / len(self.rooms) if self.rooms else 0,
        }
