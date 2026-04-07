"""SVG Renderer for house blueprints."""

import xml.etree.ElementTree as ET
from models.house import House
from models.room import Room, RoomType


class BlueprintRenderer:
    """Renders house blueprints as SVG."""
    
    ROOM_COLORS = {
        RoomType.LIVING_ROOM: '#E8F4F8',
        RoomType.KITCHEN: '#FFF8DC',
        RoomType.BEDROOM: '#E6E6FA',
        RoomType.BATHROOM: '#E0FFFF',
        RoomType.DINING_ROOM: '#F5F5DC',
        RoomType.HALLWAY: '#F0F0F0',
        RoomType.ENTRYWAY: '#FFFACD',
        RoomType.CLOSET: '#D3D3D3',
        RoomType.LAUNDRY: '#F5DEB3',
        RoomType.GARAGE: '#DCDCDC',
        RoomType.OFFICE: '#E0E0E0',
        RoomType.MASTER_BEDROOM: '#D8BFD8',
        RoomType.MASTER_BATHROOM: '#B0E0E6',
    }
    
    WALL_COLOR = '#2C3E50'
    WALL_WIDTH = 3
    DOOR_COLOR = '#8B4513'
    WINDOW_COLOR = '#87CEEB'
    
    def __init__(self, scale: float = 10.0):
        self.scale = scale
        self.padding = 50
    
    def render(self, house: House, output_path: str):
        """Render house to SVG file."""
        bounds = house.bounds
        width = (bounds[2] - bounds[0]) * self.scale + 2 * self.padding
        height = (bounds[3] - bounds[1]) * self.scale + 2 * self.padding
        
        svg = ET.Element('svg')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('width', str(width))
        svg.set('height', str(height))
        svg.set('viewBox', f'0 0 {width} {height}')
        
        # Add styles
        style = ET.SubElement(svg, 'style')
        style.text = """
            .room-label { font-family: Arial, sans-serif; font-size: 11px; font-weight: bold; }
            .room-area { font-family: Arial, sans-serif; font-size: 9px; fill: #666; }
            .title { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; }
            .subtitle { font-family: Arial, sans-serif; font-size: 11px; fill: #666; }
        """
        
        # Main group with offset
        main_group = ET.SubElement(svg, 'g')
        offset_x = self.padding - bounds[0] * self.scale
        offset_y = self.padding - bounds[1] * self.scale
        main_group.set('transform', f'translate({offset_x}, {offset_y})')
        
        # Draw rooms
        for room in house.rooms:
            self._draw_room(main_group, room)
        
        # Draw doors and windows
        for room in house.rooms:
            for door in room.doors:
                self._draw_door(main_group, room, door)
            for window in room.windows:
                self._draw_window(main_group, room, window)
        
        # Draw title
        self._draw_title(svg, house, width)
        
        # Write file
        tree = ET.ElementTree(svg)
        ET.indent(tree, space='  ')
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def _draw_room(self, parent: ET.Element, room: Room):
        """Draw a room."""
        x = room.x * self.scale
        y = room.y * self.scale
        width = room.width * self.scale
        height = room.height * self.scale
        
        # Background
        rect = ET.SubElement(parent, 'rect')
        rect.set('x', str(x))
        rect.set('y', str(y))
        rect.set('width', str(width))
        rect.set('height', str(height))
        rect.set('fill', self.ROOM_COLORS.get(room.room_type, '#FFFFFF'))
        rect.set('stroke', self.WALL_COLOR)
        rect.set('stroke-width', str(self.WALL_WIDTH))
        
        # Label
        text = ET.SubElement(parent, 'text')
        text.set('x', str(x + width / 2))
        text.set('y', str(y + height / 2 - 3))
        text.set('text-anchor', 'middle')
        text.set('class', 'room-label')
        text.text = room.name
        
        # Dimensions
        if room.area > 20:
            dim_text = ET.SubElement(parent, 'text')
            dim_text.set('x', str(x + width / 2))
            dim_text.set('y', str(y + height / 2 + 10))
            dim_text.set('text-anchor', 'middle')
            dim_text.set('class', 'room-area')
            dim_text.text = f"{room.width:.0f}' x {room.height:.0f}'"
    
    def _draw_door(self, parent: ET.Element, room: Room, door):
        """Draw a door."""
        bounds = room.bounds
        door_width = door.width * self.scale
        
        if door.wall == 'north':
            door_x = bounds[0] * self.scale + door.position * room.width * self.scale - door_width / 2
            door_y = bounds[3] * self.scale
        elif door.wall == 'south':
            door_x = bounds[0] * self.scale + door.position * room.width * self.scale - door_width / 2
            door_y = bounds[1] * self.scale
        elif door.wall == 'east':
            door_x = bounds[2] * self.scale
            door_y = bounds[1] * self.scale + door.position * room.height * self.scale - door_width / 2
        elif door.wall == 'west':
            door_x = bounds[0] * self.scale
            door_y = bounds[1] * self.scale + door.position * room.height * self.scale - door_width / 2
        else:
            return
        
        # Door opening (white line to break wall)
        line = ET.SubElement(parent, 'line')
        if door.wall in ['north', 'south']:
            line.set('x1', str(door_x))
            line.set('y1', str(door_y))
            line.set('x2', str(door_x + door_width))
            line.set('y2', str(door_y))
        else:
            line.set('x1', str(door_x))
            line.set('y1', str(door_y))
            line.set('x2', str(door_x))
            line.set('y2', str(door_y + door_width))
        line.set('stroke', 'white')
        line.set('stroke-width', str(self.WALL_WIDTH + 2))
    
    def _draw_window(self, parent: ET.Element, room: Room, window):
        """Draw a window."""
        bounds = room.bounds
        window_width = window.width * self.scale
        
        if window.wall == 'north':
            win_x = bounds[0] * self.scale + window.position * room.width * self.scale - window_width / 2
            win_y = bounds[3] * self.scale
            rect = ET.SubElement(parent, 'rect')
            rect.set('x', str(win_x))
            rect.set('y', str(win_y - 2))
            rect.set('width', str(window_width))
            rect.set('height', '4')
        elif window.wall == 'south':
            win_x = bounds[0] * self.scale + window.position * room.width * self.scale - window_width / 2
            win_y = bounds[1] * self.scale
            rect = ET.SubElement(parent, 'rect')
            rect.set('x', str(win_x))
            rect.set('y', str(win_y - 2))
            rect.set('width', str(window_width))
            rect.set('height', '4')
        elif window.wall == 'east':
            win_x = bounds[2] * self.scale
            win_y = bounds[1] * self.scale + window.position * room.height * self.scale - window_width / 2
            rect = ET.SubElement(parent, 'rect')
            rect.set('x', str(win_x - 2))
            rect.set('y', str(win_y))
            rect.set('width', '4')
            rect.set('height', str(window_width))
        elif window.wall == 'west':
            win_x = bounds[0] * self.scale
            win_y = bounds[1] * self.scale + window.position * room.height * self.scale - window_width / 2
            rect = ET.SubElement(parent, 'rect')
            rect.set('x', str(win_x - 2))
            rect.set('y', str(win_y))
            rect.set('width', '4')
            rect.set('height', str(window_width))
        else:
            return
        
        rect.set('fill', self.WINDOW_COLOR)
    
    def _draw_title(self, svg: ET.Element, house: House, canvas_width: float):
        """Draw title and stats."""
        title = ET.SubElement(svg, 'text')
        title.set('x', str(canvas_width / 2))
        title.set('y', '25')
        title.set('text-anchor', 'middle')
        title.set('class', 'title')
        title.text = house.name
        
        stats = f"{len(house.rooms)} Rooms | {house.total_area:.0f} sq ft | {house.width:.0f}' x {house.height:.0f}'"
        subtitle = ET.SubElement(svg, 'text')
        subtitle.set('x', str(canvas_width / 2))
        subtitle.set('y', '42')
        subtitle.set('text-anchor', 'middle')
        subtitle.set('class', 'subtitle')
        subtitle.text = stats
