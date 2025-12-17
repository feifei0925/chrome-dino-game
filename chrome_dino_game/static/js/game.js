// DOM元素
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('high-score');
const speedElement = document.getElementById('speed');
const gameStatus = document.getElementById('game-status');
const startBtn = document.getElementById('start-btn');
const restartBtn = document.getElementById('restart-btn');
const playerNameInput = document.getElementById('player-name');
const leaderboardList = document.getElementById('leaderboard-list');
const serverUrlElement = document.getElementById('server-url');
const localIpElement = document.getElementById('local-ip');

// 游戏状态
let gameState = 'menu';
let gameData = null;
let lastUpdate = 0;
const FPS = 60;

// 按键状态
const keys = {};

// 初始化
async function init() {
    serverUrlElement.textContent = window.location.origin;
    
    try {
        const response = await fetch('/api/get-ip');
        const data = await response.json();
        if (data.ip) {
            const url = `http://${data.ip}:${window.location.port || 5000}`;
            serverUrlElement.textContent = url;
            localIpElement.textContent = url;
        }
    } catch (error) {
        localIpElement.textContent = '无法获取IP';
    }
    
    loadLeaderboard();
    
    startBtn.addEventListener('click', startGame);
    restartBtn.addEventListener('click', restartGame);
    
    document.addEventListener('keydown', (e) => {
        keys[e.code] = true;
        handleKeyPress(e);
    });
    
    document.addEventListener('keyup', (e) => {
        keys[e.code] = false;
        if (e.code === 'ArrowDown') {
            sendDuckCommand(false);
        }
    });
    
    requestAnimationFrame(gameUpdate);
}

// 游戏主循环
function gameUpdate(timestamp) {
    const deltaTime = timestamp - lastUpdate;
    
    if (deltaTime > 1000 / FPS) {
        if (gameState === 'playing') {
            updateGame();
        }
        draw();
        lastUpdate = timestamp;
    }
    
    requestAnimationFrame(gameUpdate);
}

// 开始游戏
async function startGame() {
    const playerName = playerNameInput.value || '玩家';
    
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player_name: playerName })
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState = 'playing';
            gameData = data.game_state;
            gameStatus.innerHTML = '<h2>游戏进行中！躲避障碍物！</h2>';
            
            startBtn.disabled = true;
            restartBtn.disabled = false;
            playerNameInput.disabled = true;
            
            updateUI();
        }
    } catch (error) {
        console.error('开始游戏失败:', error);
        gameStatus.innerHTML = '<h2 style="color: red;">连接服务器失败</h2>';
    }
}

// 更新游戏状态
async function updateGame() {
    if (gameState !== 'playing') return;
    
    try {
        const response = await fetch('/api/game/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameData = data.game_state;
            
            if (gameData.state === 'game_over') {
                gameState = 'game_over';
                gameStatus.innerHTML = '<h2 style="color: red;">游戏结束！按R键重新开始</h2>';
                startBtn.disabled = true;
                restartBtn.disabled = false;
                loadLeaderboard();
            }
            
            updateUI();
        }
    } catch (error) {
        console.error('更新游戏失败:', error);
    }
}

// 处理按键
function handleKeyPress(e) {
    if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault();
        if (gameState === 'menu') {
            startGame();
        } else if (gameState === 'playing') {
            sendJumpCommand();
        } else if (gameState === 'game_over' && e.code === 'Space') {
            restartGame();
        }
    } else if (e.code === 'ArrowDown') {
        e.preventDefault();
        if (gameState === 'playing') {
            sendDuckCommand(true);
        }
    } else if (e.code === 'KeyR') {
        e.preventDefault();
        if (gameState === 'game_over') {
            restartGame();
        }
    }
}

// 发送跳跃命令
async function sendJumpCommand() {
    if (gameState !== 'playing') return;
    
    try {
        await fetch('/api/game/jump', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
    } catch (error) {
        console.error('跳跃失败:', error);
    }
}

// 发送蹲下命令
async function sendDuckCommand(isDucking) {
    if (gameState !== 'playing') return;
    
    try {
        await fetch('/api/game/duck', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ is_ducking: isDucking })
        });
    } catch (error) {
        console.error('蹲下失败:', error);
    }
}

// 重新开始游戏
async function restartGame() {
    try {
        const response = await fetch('/api/game/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState = 'playing';
            gameData = data.game_state;
            gameStatus.innerHTML = '<h2>游戏进行中！躲避障碍物！</h2>';
            restartBtn.disabled = false;
            updateUI();
        }
    } catch (error) {
        console.error('重新开始失败:', error);
    }
}

// 更新UI
function updateUI() {
    if (!gameData) return;
    
    scoreElement.textContent = gameData.score;
    highScoreElement.textContent = gameData.high_score;
    speedElement.textContent = gameData.speed.toFixed(1);
}

// 绘制游戏
function draw() {
    ctx.fillStyle = '#f1f3f4';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (!gameData) return;
    
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(0, 250, canvas.width, 50);
    
    ctx.fillStyle = 'white';
    gameData.clouds.forEach(cloud => {
        ctx.fillRect(cloud.x, cloud.y, cloud.width, cloud.height);
    });
    
    const dino = gameData.dino;
    ctx.fillStyle = dino.is_ducking ? '#FF5722' : '#4CAF50';
    ctx.fillRect(dino.x, dino.y, dino.width, dino.height);
    
    gameData.obstacles.forEach(obstacle => {
        ctx.fillStyle = obstacle.type === 'cactus' ? '#8BC34A' : '#FF9800';
        ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(
            obstacle.type === 'cactus' ? '仙人掌' : '飞鸟',
            obstacle.x + obstacle.width / 2,
            obstacle.y + obstacle.height / 2 + 4
        );
    });
    
    ctx.fillStyle = 'white';
    ctx.fillRect(dino.x + 25, dino.y + 10, 8, 8);
    ctx.fillStyle = 'black';
    ctx.fillRect(dino.x + 27, dino.y + 12, 4, 4);
}

// 加载排行榜
async function loadLeaderboard() {
    try {
        const response = await fetch('/api/leaderboard');
        const data = await response.json();
        
        if (data.leaderboard) {
            leaderboardList.innerHTML = '';
            data.leaderboard.forEach((item, index) => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span>${index + 1}. ${item.name}</span>
                    <span>${item.score} 分</span>
                `;
                leaderboardList.appendChild(li);
            });
        }
    } catch (error) {
        console.error('加载排行榜失败:', error);
        leaderboardList.innerHTML = '<li>加载排行榜失败</li>';
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', init);