from flask import Flask, render_template, request, jsonify
from game_logic import DinoGame
import uuid
import os

app = Flask(__name__)
app.secret_key = 'dino-game-secret-key'

# 存储游戏实例
games = {}

@app.route('/')
def index():
    """游戏主页"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    """开始新游戏"""
    # 生成游戏ID
    game_id = str(uuid.uuid4())
    
    # 创建新游戏实例
    game = DinoGame()
    games[game_id] = game
    
    # 返回游戏ID和初始状态
    return jsonify({
        'game_id': game_id,
        'score': game.get_score(),
        'game_state': game.get_state(),
        'message': '游戏开始！'
    })

@app.route('/api/jump', methods=['POST'])
def jump():
    """控制恐龙跳跃"""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': '游戏不存在'}), 404
    
    game = games[game_id]
    success = game.jump()
    
    return jsonify({
        'success': success,
        'score': game.get_score(),
        'game_state': game.get_state(),
        'is_game_over': game.is_game_over()
    })

@app.route('/api/update', methods=['POST'])
def update_game():
    """更新游戏状态"""
    data = request.json
    game_id = data.get('game_id')
    
    if game_id not in games:
        return jsonify({'error': '游戏不存在'}), 404
    
    game = games[game_id]
    game.update()
    
    return jsonify({
        'score': game.get_score(),
        'game_state': game.get_state(),
        'is_game_over': game.is_game_over()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
