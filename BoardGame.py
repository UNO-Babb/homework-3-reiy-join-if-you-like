import random
import time
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Constants for the grid dimensions
GRID_WIDTH = 16  # 16 columns
GRID_HEIGHT = 5  # 5 rows (height)
GRID_SIZE = GRID_WIDTH * GRID_HEIGHT  # Total cells on the grid

# Initial player state (0 means starting line)
player_positions = {
    f"player{i}": 0 for i in range(1, 6)  # Starting positions for 5 players
}

# List of players
players = [f"player{i}" for i in range(1, 6)]

# Game state variables
current_color = "red"  # Initial grid color
last_change_time = time.time()  # Time when the color was last changed
game_over = False  # Whether the game is over
winner = None  # The winner player

@app.route('/')
def index():
    return render_template('index.html', grid_width=GRID_WIDTH, grid_height=GRID_HEIGHT, player_positions=player_positions)

@app.route('/get_game_state')
def get_game_state():
    global current_color, last_change_time, game_over, winner

    # Randomly change the grid color (between red and green) every 1-10 seconds
    if time.time() - last_change_time >= random.uniform(1, 10):
        current_color = "green" if random.random() > 0.5 else "red"
        last_change_time = time.time()

    # Check if any player has won (reached the finish line)
    for player, position in player_positions.items():
        if position >= GRID_SIZE - GRID_WIDTH:  # Finish line is the last row
            game_over = True
            winner = player
            break
    
    return jsonify({
        "player_positions": player_positions,
        "current_color": current_color,
        "game_over": game_over,
        "winner": winner
    })

@app.route('/move_player', methods=['POST'])
def move_player():
    global player_positions, game_over, winner

    if game_over:
        return jsonify({"message": "Game Over!"})

    player = request.json.get('player')
    if player not in players:
        return jsonify({"error": "Invalid player"})

    # Move the player based on the grid color
    if current_color == "green":
        player_positions[player] += 1  # Move forward
    elif current_color == "red":
        player_positions[player] -= 1  # Move backward

    # Prevent player from going out of bounds
    if player_positions[player] < 0:
        player_positions[player] = 0

    # Check if any player has won
    if player_positions[player] >= GRID_SIZE - GRID_WIDTH:
        game_over = True
        winner = player
        return jsonify({
            "message": f"{player} wins!",
            "player_positions": player_positions,
            "current_color": current_color,
            "game_over": game_over,
            "winner": winner
        })

    return jsonify({
        "player_positions": player_positions,
        "current_color": current_color,
        "game_over": game_over
    })

if __name__ == '__main__':
    app.run(debug=True)
