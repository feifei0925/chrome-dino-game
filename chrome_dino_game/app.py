from flask import Flask, render_template, request, jsonify, session
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
    data = request.json
    player_name = data.get('player_name', '玩家')
    
    # 创建游戏ID
    game_id = str(uuid.uuid4())[:8]
    
    # 创建新游戏
    game = DinoGame(player_name)
    game.start_game()
    games[game_id] = game
    
    # 保存到session
    session['game_id'] = game_id
    session['player_name'] = player_name
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'game_state': game.get_state()
    })

@app.route('/api/game/update', methods=['POST'])
def update_game():
    """更新游戏状态"""
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': '游戏不存在'}), 404
    
    game = games[game_id]
    game.update()
    
    return jsonify({
        'success': True,
        'game_state': game.get_state()
    })

@app.route('/api/game/jump', methods=['POST'])
def jump():
    """恐龙跳跃"""
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': '游戏不存在'}), 404
    
    game = games[game_id]
    success = game.jump()
    
    return jsonify({
        'success': True,
        'jump_success': success,
        'game_state': game.get_state()
    })

@app.route('/api/game/duck', methods=['POST'])
def duck():
    """恐龙蹲下"""
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({'error': '游戏不存在'}), 404
    
    data = request.json
    is_ducking = data.get('is_ducking', False)
    
    game = games[game_id]
    game.duck(is_ducking)
    
    return jsonify({
        'success': True,
        'game_state': game.get_state()
    })

@app.route('/api/game/restart', methods=['POST'])
def restart_game():
    """重新开始游戏"""
    game_id = session.get('game_id')
    player_name = session.get('player_name', '玩家')
    
    # 创建新游戏
    game = DinoGame(player_name)
    game.start_game()
    
    if game_id:
        games[game_id] = game
    else:
        game_id = str(uuid.uuid4())[:8]
        games[game_id] = game
        session['game_id'] = game_id
    
    return jsonify({
        'success': True,
        'game_state': game.get_state()
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """获取排行榜"""
    leaderboard = [
        {'name': '张三', 'score': 2500},
        {'name': '李四', 'score': 1800},
        {'name': '王五', 'score': 1200},
        {'name': '玩家', 'score': 800},
    ]
    return jsonify({'leaderboard': leaderboard})

@app.route('/api/get-ip')
def get_local_ip():
    """获取本地IP地址，供局域网访问"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return jsonify({'ip': ip})
    except:
        return jsonify({'ip': 'unknown'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)