"""Blueprint Generator with customizable room placement."""

from typing import Dict, List, Any, Optional, Tuple
from models.house import House
from models.room import Room, RoomType, Direction, get_standard_size


class BlueprintGenerator:
    """Generates house blueprints with customizable room placement."""
    
    def __init__(self):
        self.layout_strategies = {
            'ranch': self._generate_ranch_layout,
            'open_concept': self._generate_open_concept_layout,
            'traditional': self._generate_traditional_layout,
            'compact': self._generate_compact_layout,
            'custom': self._generate_custom_layout,
        }
    
    def generate_house(self, config: Dict[str, Any]) -> House:
        """Generate a house blueprint from configuration."""
        style = config.get('style', 'ranch')
        house_name = config.get('name', 'Generated House')
        
        house = House(name=house_name)
        
        # Use layout strategy
        if style in self.layout_strategies:
            self.layout_strategies[style](house, config)
        else:
            self._generate_ranch_layout(house, config)
        
        # Apply custom room placements if provided
        if 'room_placements' in config:
            self._apply_custom_placements(house, config['room_placements'])
        
        # Add doors and windows
        self._add_interior_doors(house)
        self._add_exterior_windows(house)
        
        return house
    
    def _apply_custom_placements(self, house: House, placements: Dict[str, Dict]):
        """Apply custom room placements from user configuration."""
        for room_name, placement in placements.items():
            room = house.get_room(room_name)
            if room:
                # Update position
                if 'x' in placement:
                    room.x = float(placement['x'])
                if 'y' in placement:
                    room.y = float(placement['y'])
                
                # Update dimensions
                if 'width' in placement:
                    room.width = float(placement['width'])
                if 'height' in placement:
                    room.height = float(placement['height'])
                
                # Update rotation
                if 'rotation' in placement:
                    room.rotation = float(placement['rotation'])
                
                # Update preferred direction
                if 'direction' in placement:
                    direction_map = {
                        'north': Direction.NORTH,
                        'south': Direction.SOUTH,
                        'east': Direction.EAST,
                        'west': Direction.WEST,
                        'center': Direction.CENTER,
                        'north_east': Direction.NORTH_EAST,
                        'north_west': Direction.NORTH_WEST,
                        'south_east': Direction.SOUTH_EAST,
                        'south_west': Direction.SOUTH_WEST,
                    }
                    room.preferred_direction = direction_map.get(placement['direction'])
    
    def _generate_ranch_layout(self, house: House, config: Dict[str, Any]):
        """Generate a ranch-style layout."""
        bedrooms = config.get('bedrooms', 3)
        bathrooms = config.get('bathrooms', 2)
        special_rooms = config.get('special_rooms', [])
        max_width = config.get('width', 60)
        
        # Room placement preferences
        room_preferences = config.get('room_preferences', {})
        
        current_x = 0
        current_y = 0
        row_height = 0
        
        # Entryway
        entry = Room("Entryway", RoomType.ENTRYWAY, 8, 8, current_x, current_y)
        house.add_room(entry)
        current_x += 8
        row_height = 8
        
        # Living room - check preference
        living_pref = room_preferences.get('living_room', {})
        living_width = living_pref.get('width', min(18, max_width - current_x - 20))
        living_height = living_pref.get('height', 16)
        
        living = Room("Living Room", RoomType.LIVING_ROOM, living_width, living_height, current_x, current_y)
        house.add_room(living)
        current_x += living_width
        row_height = max(row_height, living_height)
        
        # Dining
        dining = Room("Dining Room", RoomType.DINING_ROOM, 12, 12, current_x, current_y)
        house.add_room(dining)
        current_x += 12
        
        # Kitchen
        kitchen = Room("Kitchen", RoomType.KITCHEN, 14, 12, current_x, current_y)
        kitchen.add_feature("Kitchen Island")
        house.add_room(kitchen)
        current_x += 14
        
        # Bedroom row
        current_y = row_height
        current_x = 0
        
        # Master bedroom
        master_pref = room_preferences.get('master_bedroom', {})
        master_width = master_pref.get('width', 16)
        master_height = master_pref.get('height', 14)
        
        master = Room("Master Bedroom", RoomType.MASTER_BEDROOM, master_width, master_height, current_x, current_y)
        house.add_room(master)
        current_x += master_width
        
        # Master bath
        master_bath = Room("Master Bathroom", RoomType.MASTER_BATHROOM, 10, 10, current_x, current_y)
        house.add_room(master_bath)
        current_x += 10
        
        # Closet
        closet = Room("Master Closet", RoomType.CLOSET, 6, 8, current_x - 6, current_y + 10)
        house.add_room(closet)
        
        # Additional bedrooms
        for i in range(1, bedrooms):
            if current_x + 12 > max_width:
                break
            bed_pref = room_preferences.get(f'bedroom_{i+1}', {})
            bed_width = bed_pref.get('width', 12)
            bed_height = bed_pref.get('height', 12)
            
            bedroom = Room(f"Bedroom {i+1}", RoomType.BEDROOM, bed_width, bed_height, current_x, current_y)
            house.add_room(bedroom)
            current_x += bed_width
        
        # Hallway
        hallway = Room("Hallway", RoomType.HALLWAY, current_x, 4, 0, current_y - 4)
        house.add_room(hallway)
        
        # Additional bathrooms
        bath_x = current_x
        for i in range(1, bathrooms):
            if bath_x + 8 > max_width:
                break
            bathroom = Room(f"Bathroom {i+1}", RoomType.BATHROOM, 8, 10, bath_x, current_y)
            house.add_room(bathroom)
            bath_x += 8
        
        # Special rooms
        self._add_special_rooms(house, special_rooms, bath_x, current_y, max_width, room_preferences)
    
    def _generate_open_concept_layout(self, house: House, config: Dict[str, Any]):
        """Generate an open-concept layout."""
        bedrooms = config.get('bedrooms', 2)
        bathrooms = config.get('bathrooms', 2)
        special_rooms = config.get('special_rooms', [])
        max_width = config.get('width', 50)
        room_preferences = config.get('room_preferences', {})
        
        # Large open area
        open_pref = room_preferences.get('living_room', {})
        open_width = open_pref.get('width', 30)
        open_height = open_pref.get('height', 20)
        
        open_area = Room("Great Room", RoomType.LIVING_ROOM, open_width, open_height, 0, 0)
        open_area.add_feature("Open Concept")
        house.add_room(open_area)
        
        # Entry
        entry = Room("Entry", RoomType.ENTRYWAY, 8, 8, open_width, 0)
        house.add_room(entry)
        
        # Kitchen attached to great room
        kitchen = Room("Kitchen", RoomType.KITCHEN, 12, 12, open_width - 12, open_height)
        house.add_room(kitchen)
        
        # Bedrooms in back
        bedroom_y = max(open_height, 20)
        current_x = 0
        
        # Master suite
        master_pref = room_preferences.get('master_bedroom', {})
        master = Room("Master Bedroom", RoomType.MASTER_BEDROOM, 
                     master_pref.get('width', 16), master_pref.get('height', 14), 
                     current_x, bedroom_y)
        house.add_room(master)
        current_x += master.width
        
        # Master bath
        master_bath = Room("Master Bath", RoomType.MASTER_BATHROOM, 10, 12, current_x, bedroom_y)
        house.add_room(master_bath)
        current_x += 10
        
        # Additional bedrooms
        for i in range(1, bedrooms):
            if current_x + 12 > max_width:
                current_x = 0
                bedroom_y += 12
            
            bed_pref = room_preferences.get(f'bedroom_{i+1}', {})
            bedroom = Room(f"Bedroom {i+1}", RoomType.BEDROOM,
                          bed_pref.get('width', 12), bed_pref.get('height', 12),
                          current_x, bedroom_y)
            house.add_room(bedroom)
            current_x += bedroom.width
        
        # Shared bathroom
        if bathrooms > 1:
            shared_bath = Room("Main Bathroom", RoomType.BATHROOM, 10, 10, open_width - 10, bedroom_y)
            house.add_room(shared_bath)
        
        # Special rooms
        self._add_special_rooms(house, special_rooms, current_x, bedroom_y, max_width, room_preferences)
    
    def _generate_traditional_layout(self, house: House, config: Dict[str, Any]):
        """Generate a traditional compartmentalized layout."""
        bedrooms = config.get('bedrooms', 3)
        bathrooms = config.get('bathrooms', 2)
        special_rooms = config.get('special_rooms', [])
        max_width = config.get('width', 50)
        room_preferences = config.get('room_preferences', {})
        
        current_x = 0
        
        # Formal living room
        living_pref = room_preferences.get('living_room', {})
        living = Room("Living Room", RoomType.LIVING_ROOM,
                     living_pref.get('width', 14), living_pref.get('height', 14),
                     current_x, 0)
        house.add_room(living)
        current_x += living.width
        
        # Dining room
        dining = Room("Dining Room", RoomType.DINING_ROOM, 12, 12, current_x, 0)
        house.add_room(dining)
        current_x += 12
        
        # Kitchen
        kitchen = Room("Kitchen", RoomType.KITCHEN, 12, 12, current_x, 0)
        house.add_room(kitchen)
        current_x += 12
        
        # Family room
        family = Room("Family Room", RoomType.LIVING_ROOM, 16, 14, 0, 14)
        house.add_room(family)
        
        # Bedrooms
        bedroom_y = 14
        current_x = 16
        
        for i in range(bedrooms):
            if current_x + 12 > max_width:
                break
            
            room_type = RoomType.MASTER_BEDROOM if i == 0 else RoomType.BEDROOM
            name = "Master Bedroom" if i == 0 else f"Bedroom {i+1}"
            
            bed_pref = room_preferences.get(f'bedroom_{i+1}' if i > 0 else 'master_bedroom', {})
            width = bed_pref.get('width', 14 if i == 0 else 12)
            
            bedroom = Room(name, room_type, width, 12, current_x, bedroom_y)
            house.add_room(bedroom)
            current_x += width
        
        # Bathrooms
        bath_y = bedroom_y + 12
        for i in range(bathrooms):
            bath_type = RoomType.MASTER_BATHROOM if i == 0 else RoomType.BATHROOM
            name = "Master Bath" if i == 0 else f"Bathroom {i+1}"
            
            bathroom = Room(name, bath_type, 10, 10, 16 + (i * 12), bath_y)
            house.add_room(bathroom)
        
        # Special rooms
        self._add_special_rooms(house, special_rooms, current_x, bedroom_y, max_width, room_preferences)
    
    def _generate_compact_layout(self, house: House, config: Dict[str, Any]):
        """Generate a compact layout."""
        bedrooms = config.get('bedrooms', 2)
        bathrooms = config.get('bathrooms', 1)
        special_rooms = config.get('special_rooms', [])
        max_width = config.get('width', 36)
        room_preferences = config.get('room_preferences', {})
        
        # Combined living area
        main_pref = room_preferences.get('living_room', {})
        main_room = Room("Living Area", RoomType.LIVING_ROOM,
                        main_pref.get('width', 24), main_pref.get('height', 14), 0, 0)
        main_room.add_feature("Combined Living/Dining")
        house.add_room(main_room)
        
        # Kitchen
        kitchen = Room("Kitchen", RoomType.KITCHEN, 10, 10, 24, 0)
        house.add_room(kitchen)
        
        # Entry
        entry = Room("Entry", RoomType.ENTRYWAY, 6, 6, 24, 10)
        house.add_room(entry)
        
        # Bedrooms
        bedroom_y = 14
        current_x = 0
        
        for i in range(bedrooms):
            room_type = RoomType.MASTER_BEDROOM if i == 0 else RoomType.BEDROOM
            name = "Master Bedroom" if i == 0 else f"Bedroom {i+1}"
            
            bed_pref = room_preferences.get(f'bedroom_{i+1}' if i > 0 else 'master_bedroom', {})
            width = bed_pref.get('width', min(14, max_width / max(bedrooms, 1)))
            
            bedroom = Room(name, room_type, width, 12, current_x, bedroom_y)
            house.add_room(bedroom)
            current_x += width
        
        # Bathrooms
        bath_x = 0
        bath_y = bedroom_y + 12
        for i in range(bathrooms):
            bath_type = RoomType.MASTER_BATHROOM if i == 0 else RoomType.BATHROOM
            name = "Master Bath" if i == 0 else f"Bath {i+1}"
            
            bathroom = Room(name, bath_type, 8, 8, bath_x, bath_y)
            house.add_room(bathroom)
            bath_x += 10
        
        # Special rooms
        self._add_special_rooms(house, special_rooms, bath_x, bath_y, max_width, room_preferences)
    
    def _generate_custom_layout(self, house: House, config: Dict[str, Any]):
        """Generate a fully custom layout based on user-defined room positions."""
        custom_rooms = config.get('custom_rooms', [])
        
        for room_data in custom_rooms:
            room = Room(
                name=room_data['name'],
                room_type=RoomType[room_data['type']],
                width=room_data['width'],
                height=room_data['height'],
                x=room_data.get('x', 0),
                y=room_data.get('y', 0),
                rotation=room_data.get('rotation', 0)
            )
            house.add_room(room)
    
    def _add_special_rooms(self, house: House, special_rooms: List[str], 
                           start_x: float, start_y: float, max_width: float,
                           room_preferences: Dict = None):
        """Add special rooms like office, laundry, garage."""
        if room_preferences is None:
            room_preferences = {}
        
        current_x = start_x
        
        for room_type in special_rooms:
            if room_type.lower() == 'office' and current_x + 10 <= max_width:
                office_pref = room_preferences.get('office', {})
                office = Room("Office", RoomType.OFFICE,
                             office_pref.get('width', 10), office_pref.get('height', 10),
                             current_x, start_y)
                house.add_room(office)
                current_x += office.width
            
            elif room_type.lower() == 'laundry':
                laundry_pref = room_preferences.get('laundry', {})
                laundry = Room("Laundry", RoomType.LAUNDRY,
                              laundry_pref.get('width', 6), laundry_pref.get('height', 8),
                              current_x, start_y)
                house.add_room(laundry)
                current_x += laundry.width
            
            elif room_type.lower() == 'garage':
                garage_pref = room_preferences.get('garage', {})
                garage = Room("Garage", RoomType.GARAGE,
                             garage_pref.get('width', 20), garage_pref.get('height', 22),
                             -22, 0)
                garage.add_feature("2-Car Garage")
                house.add_room(garage)
    
    def _add_interior_doors(self, house: House):
        """Add doors between adjacent rooms."""
        rooms = house.rooms
        
        for i, room1 in enumerate(rooms):
            for room2 in rooms[i + 1:]:
                adjacency = self._get_adjacency(room1, room2)
                if adjacency:
                    wall1, wall2, position = adjacency
                    room1.add_door(wall1, position, leads_to=room2.name)
                    room2.add_door(wall2, 1 - position, leads_to=room1.name)
    
    def _get_adjacency(self, room1: Room, room2: Room) -> Optional[Tuple[str, str, float]]:
        """Check if two rooms are adjacent."""
        b1 = room1.bounds
        b2 = room2.bounds
        tolerance = 0.5
        
        # North-south adjacency
        if abs(b1[3] - b2[1]) < tolerance or abs(b2[3] - b1[1]) < tolerance:
            x_overlap_start = max(b1[0], b2[0])
            x_overlap_end = min(b1[2], b2[2])
            if x_overlap_start < x_overlap_end:
                position = (x_overlap_start + x_overlap_end) / 2
                if b1[3] > b2[3]:
                    return ('south', 'north', (position - b1[0]) / room1.width)
                else:
                    return ('north', 'south', (position - b1[0]) / room1.width)
        
        # East-west adjacency
        if abs(b1[2] - b2[0]) < tolerance or abs(b2[2] - b1[0]) < tolerance:
            y_overlap_start = max(b1[1], b2[1])
            y_overlap_end = min(b1[3], b2[3])
            if y_overlap_start < y_overlap_end:
                position = (y_overlap_start + y_overlap_end) / 2
                if b1[2] > b2[2]:
                    return ('west', 'east', (position - b1[1]) / room1.height)
                else:
                    return ('east', 'west', (position - b1[1]) / room1.height)
        
        return None
    
    def _add_exterior_windows(self, house: House):
        """Add windows to exterior walls."""
        bounds = house.bounds
        
        for room in house.rooms:
            b = room.bounds
            
            if abs(b[3] - bounds[3]) < 1:
                room.add_window('north', 0.5)
            if abs(b[1] - bounds[1]) < 1:
                room.add_window('south', 0.5)
            if abs(b[2] - bounds[2]) < 1:
                room.add_window('east', 0.5)
            if abs(b[0] - bounds[0]) < 1:
                room.add_window('west', 0.5)
