from flask import Flask, render_template, jsonify, request, session
import random
import json

app = Flask(__name__, template_folder='.')
app.secret_key = 'retro_arcade_secret_2024'

# ─── Word list for Hangman ───────────────────────────────────────────────────
HANGMAN_WORDS = [
    'python', 'javascript', 'arcade', 'pixel', 'retro', 'galaxy',
    'quantum', 'nebula', 'crystal', 'phantom', 'vortex', 'eclipse',
    'dragon', 'wizard', 'castle', 'knight', 'shield', 'sword',
    'treasure', 'dungeon', 'monster', 'potion', 'magic', 'spell',
    'portal', 'quest', 'legend', 'hero', 'villain', 'adventure'
]

# ─── Solitaire deck helper ────────────────────────────────────────────────────
def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = []
    for suit in suits:
        for rank in ranks:
            color = 'red' if suit in ['♥', '♦'] else 'black'
            value = ranks.index(rank) + 1
            deck.append({'suit': suit, 'rank': rank, 'color': color, 'value': value, 'face_up': False})
    random.shuffle(deck)
    return deck

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<game_name>')
def game(game_name):
    return render_template(f'{game_name}.html')

# ── Hangman API ──────────────────────────────────────────────────────────────
@app.route('/api/hangman/new', methods=['POST'])
def hangman_new():
    word = random.choice(HANGMAN_WORDS).upper()
    session['hangman_word'] = word
    session['hangman_guessed'] = []
    session['hangman_wrong'] = 0
    return jsonify({
        'length': len(word),
        'display': ['_'] * len(word),
        'wrong': 0,
        'max_wrong': 6,
        'guessed': []
    })

@app.route('/api/hangman/guess', methods=['POST'])
def hangman_guess():
    data = request.json
    letter = data.get('letter', '').upper()
    word = session.get('hangman_word', '')
    guessed = session.get('hangman_guessed', [])
    wrong = session.get('hangman_wrong', 0)

    if not letter or letter in guessed:
        return jsonify({'error': 'Already guessed or invalid'}), 400

    guessed.append(letter)
    if letter not in word:
        wrong += 1

    session['hangman_guessed'] = guessed
    session['hangman_wrong'] = wrong

    display = [c if c in guessed else '_' for c in word]
    won = '_' not in display
    lost = wrong >= 6

    return jsonify({
        'display': display,
        'wrong': wrong,
        'max_wrong': 6,
        'guessed': guessed,
        'correct': letter in word,
        'won': won,
        'lost': lost,
        'word': word if (won or lost) else None
    })

# ── Solitaire API ────────────────────────────────────────────────────────────
@app.route('/api/solitaire/new', methods=['POST'])
def solitaire_new():
    deck = create_deck()
    tableau = [[] for _ in range(7)]
    for col in range(7):
        for row in range(col + 1):
            card = deck.pop()
            card['face_up'] = (row == col)
            tableau[col].append(card)
    # Remaining cards go to stock
    stock = deck
    return jsonify({
        'tableau': tableau,
        'stock': [{'face_up': False} for _ in stock],
        'stock_data': stock,
        'waste': [],
        'foundations': [[], [], [], []]
    })

# ── Snake and Ladders API ────────────────────────────────────────────────────
@app.route('/api/snl/roll', methods=['POST'])
def snl_roll():
    data = request.json
    position = data.get('position', 0)
    die = random.randint(1, 6)
    new_pos = position + die
    if new_pos > 100:
        new_pos = position  # Can't exceed 100

    # Snakes
    snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}
    # Ladders
    ladders = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}

    event = None
    final_pos = new_pos
    if new_pos in snakes:
        final_pos = snakes[new_pos]
        event = 'snake'
    elif new_pos in ladders:
        final_pos = ladders[new_pos]
        event = 'ladder'

    won = final_pos == 100
    return jsonify({'die': die, 'position': final_pos, 'event': event, 'won': won, 'intermediate': new_pos})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
