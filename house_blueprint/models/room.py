"""Room model with placement and direction controls."""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


class RoomType(Enum):
    LIVING_ROOM = "Living Room"
    KITCHEN = "Kitchen"
    BEDROOM = "Bedroom"
    BATHROOM = "Bathroom"
    DINING_ROOM = "Dining Room"
    HALLWAY = "Hallway"
    ENTRYWAY = "Entryway"
    CLOSET = "Closet"
    LAUNDRY = "Laundry"
    GARAGE = "Garage"
    OFFICE = "Office"
    MASTER_BEDROOM = "Master Bedroom"
    MASTER_BATHROOM = "Master Bath"


class Direction(Enum):
    """Cardinal directions for room placement."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTER = "center"
    NORTH_EAST = "north_east"
    NORTH_WEST = "north_west"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"


@dataclass
class Door:
    wall: str
    position: float = 0.5
    width: float = 3.0
    leads_to: Optional[str] = None


@dataclass
class Window:
    wall: str
    position: float = 0.5
    width: float = 4.0
    height: float = 4.0


@dataclass
class Room:
    name: str
    room_type: RoomType
    width: float
    height: float
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # Rotation in degrees
    preferred_direction: Optional[Direction] = None
    doors: List[Door] = field(default_factory=list)
    windows: List[Window] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def add_door(self, wall: str, position: float = 0.5, 
                 width: float = 3.0, leads_to: Optional[str] = None) -> 'Room':
        self.doors.append(Door(wall, position, width, leads_to))
        return self
    
    def add_window(self, wall: str, position: float = 0.5,
                   width: float = 4.0, height: float = 4.0) -> 'Room':
        self.windows.append(Window(wall, position, width, height))
        return self
    
    def add_feature(self, feature: str) -> 'Room':
        """Add a special feature to the room."""
        self.features.append(feature)
        return self
    
    def intersects(self, other: 'Room', padding: float = 0.0) -> bool:
        b1 = self.bounds
        b2 = other.bounds
        return not (
            b1[2] + padding <= b2[0] or b1[0] >= b2[2] + padding or
            b1[3] + padding <= b2[1] or b1[1] >= b2[3] + padding
        )


# Standard sizes
STANDARD_SIZES = {
    RoomType.LIVING_ROOM: (16, 20),
    RoomType.KITCHEN: (12, 14),
    RoomType.BEDROOM: (12, 12),
    RoomType.BATHROOM: (8, 10),
    RoomType.DINING_ROOM: (12, 14),
    RoomType.HALLWAY: (4, 10),
    RoomType.ENTRYWAY: (6, 8),
    RoomType.CLOSET: (4, 6),
    RoomType.LAUNDRY: (6, 8),
    RoomType.GARAGE: (20, 24),
    RoomType.OFFICE: (10, 12),
    RoomType.MASTER_BEDROOM: (16, 18),
    RoomType.MASTER_BATHROOM: (10, 12),
}


def get_standard_size(room_type: RoomType) -> Tuple[float, float]:
    return STANDARD_SIZES.get(room_type, (10, 10))
