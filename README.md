# AI Pathfinder - Informed Search Visualization

## Project Overview

This project implements an **AI Pathfinder** that visualizes how different informed search algorithms explore a grid environment to find the optimal path from a start point to a goal point while avoiding static obstacles and adapting to dynamically spawning obstacles.

The application features a **step-by-step GUI visualization** that shows exactly how each algorithm "thinks"—which nodes it explores, which it ignores, and the final path it chooses.

## Team Members
- **Muhammad Saad Fareed** (23F-0865)

**Course:** AI 2002 - Artificial Intelligence  
**Instructor:** Dr. Hashim Yaseen  
**University:** FAST-NUCES, CFD Campus  
**Semester:** Spring 2026

---

## Features

✅ **2 informed Search Algorithms Implemented:**
- Greedy Best-First Search (BFS)
- A* Search

✅ **Dynamic Grid Environment:**
- Static obstacles (walls)
- Dynamic obstacles that spawn during algorithm execution
- Intelligent re-planning when paths are blocked

✅ **Advanced GUI Visualization (Pygame):**
- Step-by-step animation of search process
- Real-time frontier and explored node tracking
- Final path highlighting
- Statistics panel showing:
  - Nodes explored
  - Path length
  - Execution time
  - Dynamic obstacles encountered
  - Number of re-plans triggered
- Color-coded legend

✅ **6-Direction Movement Order:**
- Up, Right, Bottom, Bottom-Right (diagonal), Left, Top-Left (diagonal)
- Smart diagonal validation (prevents corner cutting)
- Consistent node expansion order

✅ **Accurate Cost Calculation:**
- Cardinal movements: 1.0 cost
- Diagonal movements: √2 ≈ 1.414 cost

---

## Requirements

- **Python:** 3.13.11 or higher
- **Pygame:** 2.6.1
- **Operating System:** Any Windows, Any Linux Distro, Any Macintosh or compatible

---

## Installation

### Option 1: Using requirements.txt (Recommended)

1. **Clone or download the project**
2. **Open Command Prompt** in the project directory
3. **Install dependencies:**
```bash

   pip install -r informed_requirements.txt
```

### Option 2: Install pygame directly
```bash
pip install pygame==2.6.1
```

### Verify Installation

Check if pygame is installed correctly in Ubuntu Terminal:
```bash
pip show pygame
```

You should see:
```
Version: 2.6.1
```

---

## How to Run

1. **Open Command Prompt** in the project directory
2. **Run the application:**
```bash
   python main.py
```
3. **Select an algorithm** from the UI
4. **Watch the visualization** as the algorithm explores the grid
5. **Close the window** to return to the menu

---

## Project Structure
```
AI_A2_23F_0865/
│
├── informed_main.py                 # Main application entry point and menu
├── informed_grid.py                 # Grid class with obstacle management
├── informed_search.py               # All 6 search algorithm implementations
├── informed_viz.py                  # Pygame visualization and GUI
├── informed_requirements.txt        # Python package dependencies
└── README.md                        # This file
```

### File Descriptions

| File | Purpose |
|------|---------|
| `informed_main.py` | Menu system, algorithm selection, and result display |
| `informed_grid.py` | Grid initialization, obstacle spawning, pathfinding helpers |
| `informed_search.py` | All 6 search algorithm implementations with re-planning |
| `informed_viz.py` | Pygame GUI, animation, statistics panel, visualization |
| `informed_requirements.txt` | Package dependencies (pygame==2.6.1) |

---

## Algorithm Details

### Greedy Best-First Search (BFS)
- **Time Complexity:** O(b^m)
- **Space Complexity:** O(b^m)
- **Optimal:** No
- **Complete:** Yes (under some conditions, otherwise No)
- **Use Case:** Finding shortest path in with heuristics

### A* Search
- **Time Complexity:** O(b^h*-h)
- **Space Complexity:** O(b^h*-h) - height of tree
- **Optimal:** Yes
- **Complete:** Yes
- **Use Case:** Finding shortest path with evaluation function
---

## GUI Controls

### Window Title
`GOOD PERFORMANCE TIME APP`

### Colors Used
- 🟩 **Green** - Start position
- 🟥 **Red** - Goal position
- 🟨 **Yellow** - Explored nodes
- 🟦 **Light Blue** - Frontier nodes
- 🟦 **Dark Blue** - Final path
- 🟧 **Orange** - Dynamic obstacles
- ⬛ **Black** - Static walls

### How to Close
- Click the **X button** on the window, or
- Press **ESC** key

---

## Dynamic Obstacles & Re-planning

### How It Works

1. **Static Obstacles** - Added at grid initialization (10% probability)
2. **Dynamic Obstacles** - Spawn during algorithm execution (2% probability per step)
3. **Detection** - Algorithm checks if current path is blocked
4. **Re-planning** - When blocked, algorithm restarts search from current position

### Console Output Example
```
⚠️ Dynamic obstacle spawned at (7, 4)
🔄 Re-planning: Path blocked at (7, 4)
```

---

## Key Implementation Details

### Movement Order (Strict Clockwise)
```
1. Up (-1, 0)
2. Right (0, 1)
3. Bottom (1, 0)
4. Bottom-Right (1, 1) [Diagonal]
5. Left (0, -1)
6. Top-Left (-1, -1) [Diagonal]
```

### Diagonal Validation
- Both adjacent cardinal cells must be clear before allowing diagonal movement
- Prevents "corner cutting" through tight passages
---

## Troubleshooting

### Issue: "pygame not found"
**Solution:**
```bash
pip install pygame==2.6.1
```

### Issue: "ModuleNotFoundError: No module named 'pygame'"
**Solution:**
```bash
pip install --upgrade pygame
```

### Issue: Window doesn't appear
**Solution:**
- Check if pygame is installed: `pip show pygame`
- Ensure you're in the correct directory: `cd path/to/project`
- Try running again: `python main.py`

### Issue: Algorithm runs very slowly
**Solution:**
- This is normal, especially for IDDFS with many dynamic obstacles
- Close other applications to free up resources
---

## Future Enhancements

- [ ] Adjustable grid size
- [ ] Adjustable obstacle probability
- [ ] Save/load grid configurations
- [ ] Performance comparison charts
- [ ] A* algorithm with heuristics
- [ ] Step-by-step pause/resume
- [ ] Export path as image

---

## Viva Voce Preparation

This implementation demonstrates:

1. **Algorithm Understanding**
   - Each algorithm correctly implements its strategy
   - Proper data structure usage (queues, stacks, priority queues)

2. **Advanced Features**
   - Dynamic obstacle handling
   - Real-time re-planning
   - Cost-aware pathfinding

3. **Code Quality**
   - Clean, modular structure
   - Comprehensive comments
   - Proper error handling

4. **GUI Development**
   - Professional visualization
   - Real-time animation
   - Statistical tracking

---

## References

- Russell, S., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.)
- Pygame Documentation: https://www.pygame.org/docs/
- Python Documentation: https://docs.python.org/3/

---

## License

This project was developed as part of AI 2002 course assignment at FAST-NUCES.

---

## Contact

For questions or issues:
- **Muhammad Saad Fareed: f230865@cfd.nu.edu.pk** 23F-0865

---
**Last Updated:** February 28, 2026
