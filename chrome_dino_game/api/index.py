from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chrome恐龙游戏</title>
        <style>
            body { text-align: center; padding: 50px; font-family: Arial; }
            canvas { border: 2px solid black; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>🦖 Chrome小恐龙游戏 - Vercel部署版</h1>
        <canvas id="game" width="800" height="300"></canvas>
        <p>分数: <span id="score">0</span></p>
        <p>空格键跳跃 | ↓蹲下 | R重新开始</p>
        
        <script>
            const canvas = document.getElementById('game');
            const ctx = canvas.getContext('2d');
            let score = 0;
            let dinoY = 200;
            
            function draw() {
                ctx.clearRect(0, 0, 800, 300);
                // 画恐龙
                ctx.fillStyle = 'green';
                ctx.fillRect(100, dinoY, 40, 60);
                // 显示分数
                ctx.fillStyle = 'black';
                ctx.font = '24px Arial';
                ctx.fillText('分数: ' + score, 20, 40);
            }
            
            document.addEventListener('keydown', (e) => {
                if (e.code === 'Space') {
                    score++;
                    document.getElementById('score').textContent = score;
                    draw();
                }
            });
            
            draw();
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)