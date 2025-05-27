
![](./assets/project-thumb.png)

# 🚦 Smart Traffic Simulation - Project Overview

A simulation of a traffic intersection using **Pygame**, showcasing vehicles, traffic lights, and congestion control.

---

## 🧩 Modules Used

- `pygame`: Rendering graphics, input, and audio
- `random`: Spawning vehicles randomly
- `asyncio`: Asynchronous main loop
- `platform`: Detect if running in a browser (via Emscripten)

---

## 🖥️ Screen Setup

- **Resolution**: `WIDTH = 1366`, `HEIGHT = 768`
- Title: `Smart Traffic Simulation || CSC 455 Project`
- Optional background image: `assets/road_background.png`

---

## 🎨 Constants & Configuration

### Colors
```python
WHITE, BLACK, RED, GREEN, YELLOW, BLUE, LIGHT_BLUE, DARK_GRAY
```

### Road
- `ROAD_WIDTH = 200`
- `LANE_WIDTH = ROAD_WIDTH // 2`
- `INTERSECTION_X`, `INTERSECTION_Y` center of the screen

### Vehicles
Stored in `vehicle_sizes`:
```python
car, bus, bike, cng
```
Each with width, height, and speed

### Traffic Lights
- Four directions: top, bottom, right, left
- State: `red`, `green`, or `yellow`
- Timer: `30 seconds` per light (1800 frames at 60 FPS)

---

## 🚗 Vehicle Class

```python
class Vehicle:
    def __init__(...):  # initializes vehicle
    def move():         # moves if light is green
    def draw(screen):   # draws image or fallback box
```

- Attributes: `rect`, `direction`, `lane`, `vehicle_type`, `speed`, `image`
- Rotation applied based on direction

---

## 🔧 Game Functions

### `draw_menu()`
Displays start menu with:
- "Start Simulation"
- "Instructions"
- "Exit"

### `draw_traffic_lights()`
Draws vertical/horizontal light bars with active color indicators and timer values.

### `draw_hud()`
Displays:
- Score status (`Excellent`, `Moderate`, `Needs Improvement`)
- Congestion level
- Current mode (Day/Night)

### `spawn_vehicle()`
Random chance (5%) to spawn a vehicle from a random direction:
- Type: `car`, `bus`, `bike`, `cng`
- Lane and coordinates calculated accordingly

### `update_congestion()`
- Checks number of vehicles near the intersection
- Updates:
  - `congestion_level`
  - `score`
  - `score_text` feedback

### `setup()`
Resets game variables for a new session.

---

## 🕹️ Game Loop

```python
async def update_loop():
```
Main simulation loop:
- Handles all user input
- Updates lights, vehicles, drawing
- Runs at **60 FPS**

### Keyboard Controls:
- `Enter`: Select menu option
- `↑ ↓`: Navigate menu
- `G`: Toggle all lights (red/green)
- `D`: Toggle day/night mode

---

## 🔊 Audio

- Background sound: `audio/road-noise.mp3`
- Played in a loop during simulation
- Controlled with `pygame.mixer`

---

## 🌍 Platform Detection

```python
if platform.system() == "Emscripten":
    asyncio.ensure_future(update_loop())  # for browsers
else:
    asyncio.run(update_loop())  # for desktop
```

---

## 📁 Folder Structure (Expected)

```
project/
├── assets/
│   ├── road_background.png
│   ├── car.png
│   ├── bus.png
│   ├── bike.png
│   └── cng.png
├── audio/
│   └── road-noise.mp3
└── main.py
```

---

## ✅ Features Summary

| Feature             | Description                             |
|--------------------|-----------------------------------------|
| Vehicle Types       | Car, Bus, Bike, CNG                     |
| Light Control       | Automatic & Manual (G key)             |
| Congestion Feedback | Score + Visual label                   |
| Menu UI             | Start, Instructions, Exit              |
| Day/Night Mode      | Toggle using `D` key                   |
| Background Audio    | Ambient road noise                     |
| Collision Handling  | Vehicles removed on same-lane collision|
| Cross-Platform      | Emscripten/browser & Desktop           |

---

## Installation

### Windows

1. Clone the repository:
    ```console
    git clone https://github.com/0xh7ml/trafficgame.git
    ```
2. Navigate to the project directory:
    ```console
    cd trafficgame
    ```
3. Install dependencies (using Python and pip as an example):
    ```console
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

### Linux

1. Clone the repository:
    ```console
    git clone https://github.com/0xh7ml/trafficgame.git
    ```
2. Navigate to the project directory:
    ```console
    cd trafficgame
    ```
3. Install dependencies:
    ```console
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

### Project Structure
    assets:
       - vehicle image, background image
    audio:
       - vehicle sound
    main.py: game file
    requirements.txt: dependency file