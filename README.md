## ⚽ Arcade Football Simulation Engine
An advanced, modular 11v11 sports simulation engine engineered from scratch in **Python** and **Pygame**. Designed with clean separation of concerns, this project blends classic retro arcade aesthetics (inspired by titles like *Sensible Soccer*) with modern artificial intelligence techniques, including role-based tactical decision trees, Boids obstacle avoidance, and specialized goalkeeper state machines.


# ⚽ 11v11 Arcade Football Simulation Engine

A professional-grade, modular arcade-style football simulation built from scratch in **Python** using **Pygame**. Inspired by classic retro sports games, this engine features a massive virtual pitch, a dynamic camera system, advanced role-based artificial intelligence, and custom sprite animation processing.

---

## 🚀 Key Features

* **Modular Architecture**: Cleanly decoupled source code separating global configurations (`config.py`), object-oriented entity physics & AI (`entities.py`), and the primary execution loop (`main.py`).
* **Massive Virtual Pitch & Radar**: A virtual 2400x1500 pixel turf featuring smooth camera bounding and a real-time transparent HUD radar/minimap mapping all 22 players and the ball.
* **Role-Based Tactical AI**: 
  * **Boids Separation**: Prevents CPU and human teammates from swarming or overlapping by calculating real-time repulsion forces.
  * **Dynamic Pressing**: Automatically assigns the single closest player to press the ball while the rest of the team holds a structured 4-3-3 formation.
  * **Goalkeeper State Machine**: A dedicated bounding constraint engine that forces goalkeepers to lock onto the goal line, track the ball's Y-coordinate, and aggressively defend the penalty box danger zone.
  * **Attacking Decision Tree**: CPU players evaluate scoring opportunities, execute high-velocity shots, and calculate open passing lanes.
* **Retro Sprite Animation Engine**: Custom sprite-sheet slicing that extracts idle frames and 6-frame running loops, complete with dynamic vector flipping (`pygame.transform.flip`) and procedural dust-trail particle effects.
* **Global Audio Engine**: Integrated Pygame mixer managing spatial sound effects for ball impacts, referee whistles, and crowd reactions.

---

## 📁 Project Directory Structure

```text
football/
│
├── assets/
│   ├── sounds/
│   │   ├── kick.mp3
│   │   ├── whistle.mp3
│   │   └── crowd.mp3
│   │
│   └── sprites/
│       ├── player_blue.png
│       └── player_red.png
│
├── src/
│   ├── config.py       # Global settings, dimensions, and audio mixer setup
│   └── entities.py     # Ball, Player, AI logic, and sprite animation engine
│
├── main.py             # Match engine states, camera rendering, and game loop
└── requirements.txt    # Project dependencies
🛠️ Installation & Setup
Clone the Repository:

Bash
git clone [https://github.com/SyedRazaZaidi/arcade-football-simulation.git](https://github.com/SyedRazaZaidi/arcade-football-simulation.git)
cd football
Install Dependencies:
Ensure you have Python installed, then install Pygame:

Bash
pip install -r requirements.txt
Verify Assets:
Make sure your sprite sheets and audio tracks are placed correctly inside the assets/sprites/ and assets/sounds/ folders as defined in the directory structure.

Run the Simulation:

Bash
python main.py
🎮 Game Controls
Move Player: W, A, S, D (Controls the active player nearest to the ball)

Pass to Teammate: Press Q when close to the ball

Charge & Shoot: Hold SPACE to power up your shot, release to fire
