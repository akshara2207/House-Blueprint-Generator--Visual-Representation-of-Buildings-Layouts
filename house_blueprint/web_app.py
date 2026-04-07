"""
Web Application for House Blueprint Generator with Room Customization.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime

from models.house import House
from models.room import Room, RoomType, Direction
from generator.blueprint_generator import BlueprintGenerator
from visualization.renderer import BlueprintRenderer

app = Flask(__name__)

# Initialize components
generator = BlueprintGenerator()
renderer = BlueprintRenderer(scale=8)

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'generated')
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route('/')
def index():
    """Main page with room customization."""
    presets = {
        'cozy_cottage': {'name': 'Cozy Cottage', 'bedrooms': 2, 'bathrooms': 1, 'style': 'traditional'},
        'family_home': {'name': 'Family Home', 'bedrooms': 3, 'bathrooms': 2, 'style': 'ranch'},
        'modern_loft': {'name': 'Modern Loft', 'bedrooms': 2, 'bathrooms': 2, 'style': 'open_concept'},
        'mansion': {'name': 'Luxury Estate', 'bedrooms': 5, 'bathrooms': 4, 'style': 'traditional'},
    }
    
    styles = [
        ('ranch', 'Ranch Style'),
        ('open_concept', 'Open Concept'),
        ('traditional', 'Traditional'),
        ('compact', 'Compact'),
    ]
    
    room_types = [
        ('office', 'Office'),
        ('laundry', 'Laundry Room'),
        ('garage', 'Garage'),
    ]
    
    directions = [
        ('north', 'North (Top)'),
        ('south', 'South (Bottom)'),
        ('east', 'East (Right)'),
        ('west', 'West (Left)'),
        ('center', 'Center'),
        ('north_east', 'North East'),
        ('north_west', 'North West'),
        ('south_east', 'South East'),
        ('south_west', 'South West'),
    ]
    
    return render_template('index.html', 
                         presets=presets, 
                         styles=styles,
                         room_types=room_types,
                         directions=directions)


@app.route('/generate', methods=['POST'])
def generate_blueprint():
    """Generate blueprint with custom room placements."""
    try:
        data = request.get_json()
        
        # Build configuration
        config = {
            'name': data.get('name', 'My House'),
            'style': data.get('style', 'ranch'),
            'bedrooms': int(data.get('bedrooms', 3)),
            'bathrooms': int(data.get('bathrooms', 2)),
            'width': int(data.get('width', 50)),
            'special_rooms': data.get('special_rooms', []),
        }
        
        # Add room preferences for sizes and directions
        if 'room_preferences' in data:
            config['room_preferences'] = data['room_preferences']
        
        # Add custom room placements
        if 'room_placements' in data:
            config['room_placements'] = data['room_placements']
        
        # Generate house
        house = generator.generate_house(config)
        
        # Generate SVG
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"blueprint_{timestamp}.svg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        renderer.render(house, filepath)
        
        # Read SVG content
        with open(filepath, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Get statistics
        stats = house.get_statistics()
        
        # Get room list with positions
        rooms_list = []
        for room in house.rooms:
            rooms_list.append({
                'name': room.name,
                'type': room.room_type.value,
                'width': room.width,
                'height': room.height,
                'x': room.x,
                'y': room.y,
                'area': round(room.area, 1),
            })
        
        return jsonify({
            'success': True,
            'svg': svg_content,
            'filename': filename,
            'stats': {
                'total_rooms': stats['total_rooms'],
                'total_area': round(stats['total_area'], 1),
                'dimensions': stats['dimensions'],
                'average_room_size': round(stats['average_room_size'], 1),
            },
            'rooms': rooms_list,
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/editor')
def editor():
    """Interactive drag-and-drop editor."""
    return render_template('editor.html')


@app.route('/update-layout', methods=['POST'])
def update_layout():
    """Update blueprint with custom room positions from editor."""
    try:
        data = request.get_json()
        rooms_data = data.get('rooms', [])
        
        # Create house from room data
        house = House(name="Custom Layout")
        
        # Room type mapping
        type_mapping = {
            'LIVING ROOM': RoomType.LIVING_ROOM,
            'KITCHEN': RoomType.KITCHEN,
            'BEDROOM': RoomType.BEDROOM,
            'BATHROOM': RoomType.BATHROOM,
            'DINING ROOM': RoomType.DINING_ROOM,
            'HALLWAY': RoomType.HALLWAY,
            'ENTRYWAY': RoomType.ENTRYWAY,
            'CLOSET': RoomType.CLOSET,
            'LAUNDRY': RoomType.LAUNDRY,
            'GARAGE': RoomType.GARAGE,
            'OFFICE': RoomType.OFFICE,
            'MASTER BEDROOM': RoomType.MASTER_BEDROOM,
            'MASTER BATH': RoomType.MASTER_BATHROOM,
            'MASTER BATHROOM': RoomType.MASTER_BATHROOM,
        }
        
        for room_data in rooms_data:
            room_type_str = room_data.get('type', 'BEDROOM').upper()
            room_type = type_mapping.get(room_type_str, RoomType.BEDROOM)
            
            room = Room(
                name=room_data['name'],
                room_type=room_type,
                width=float(room_data['width']),
                height=float(room_data['height']),
                x=float(room_data['x']),
                y=float(room_data['y'])
            )
            house.add_room(room)
        
        # Add doors between adjacent rooms
        generator._add_interior_doors(house)
        generator._add_exterior_windows(house)
        
        # Generate SVG
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"blueprint_custom_{timestamp}.svg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        renderer.render(house, filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Layout saved successfully'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/download/<filename>')
def download_blueprint(filename):
    """Download SVG file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/svg+xml', as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    print("=" * 60)
    print("House Blueprint Generator - Web Interface")
    print("=" * 60)
    print("Open your browser and navigate to: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
