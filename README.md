# AlgoLab

A desktop application developed with Pygame for visualizing data structures and algorithms built for Data Structure course. Every topic shows a step-by-step, pausable, rewindable animation of each operation, alongside a live explanation of what is happening and why.

## Topics

- **Asymptotic Notation:** complexity graphs with adjustable inputs
- **Linked Lists:** insert, delete, search
- **Stacks:** push, pop, peek
- **Queues:** enqueue, dequeue, peek
- **Binary Search Trees:** insert, search, delete, min/max, different traversal ordering of the tree
- **Heaps:** insert, peek, extract, min/max, heapify
- **Graphs:** directed/undirected, weighted/unweighted toggles, BFS, DFS, Dijkstra, B-F
- **Sorting:** BubbleSort, InsertionSort, MergeSort, QuickSort, HeapSort
- **Hash Tables & Sets:** Chaining, Probings, DH, Set/Map modes, adjustable hash functions, collisions counter

## Features

- Step-by-step animation with settings/control over the DS attributes
- Adjustable speed over animation
- Live "what is happening" explanation
- Color-coded operation + legends
- A **Randomize** button for every topic to initialize the DS randomly
- Some keyboard shorcuts: `P` to pause/play, `<-`/`->` to step backward/forward in animation, `Enter` to run the primary action of each topic

## Requirements

- Python 3.10+
- [Pygame](https://www.pygame.org/)

## Getting Started
1. Clone and enter the repository:
```bash
git clone https://github.com/AmirmasoudCS/AlgoLab.git
cd AlgoLab
```
2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```
3. Install the dependencies:
```bash
pip install -r requirements.txt
```
4. Run the application:
```bash
python -m algolab.main
```


## Project structure

```text
📁 
├── 📁 assets
│   ├── 📄 icon.ico
│   └── 🖼️ icon.png
├── 📁 config
│   └── ⚙️ config.toml
├── 📁 log
├── 📁 src
│   └── 📁 algolab
│       ├── 📁 core
│       │   ├── 🐍 __init__.py
│       │   ├── 🐍 application.py
│       │   └── 🐍 configuration.py
│       ├── 📁 simulation
│       │   ├── 🐍 __init__.py
│       │   ├── 🐍 events.py
│       │   ├── 🐍 history.py
│       │   ├── 🐍 simulator.py
│       │   └── 🐍 state.py
│       ├── 📁 topics
│       │   ├── 📁 asymptotic
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 complexity.py
│       │   │   ├── 🐍 model.py
│       │   │   └── 🐍 visualizer.py
│       │   ├── 📁 bst
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 graph
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 hash_table
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 heap
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 linked_list
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 queue
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 sorting
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   ├── 📁 stack
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 model.py
│       │   │   ├── 🐍 operations.py
│       │   │   └── 🐍 simulation.py
│       │   └── 🐍 __init__.py
│       ├── 📁 ui
│       │   ├── 📁 components
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 button.py
│       │   │   ├── 🐍 checkbox.py
│       │   │   ├── 🐍 numeric_input.py
│       │   │   ├── 🐍 radio_button.py
│       │   │   └── 🐍 surface.py
│       │   ├── 📁 screens
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 asymptotic.py
│       │   │   ├── 🐍 bst.py
│       │   │   ├── 🐍 graph.py
│       │   │   ├── 🐍 hash_table.py
│       │   │   ├── 🐍 heap.py
│       │   │   ├── 🐍 linked_list.py
│       │   │   ├── 🐍 main_menu.py
│       │   │   ├── 🐍 queue.py
│       │   │   ├── 🐍 screen.py
│       │   │   ├── 🐍 screen_manager.py
│       │   │   ├── 🐍 sorting.py
│       │   │   └── 🐍 stack.py
│       │   ├── 🐍 __init__.py
│       │   └── 🐍 theme.py
│       ├── 📁 visualization
│       │   ├── 📁 graph
│       │   │   ├── 🐍 __init__.py
│       │   │   ├── 🐍 bounds.py
│       │   │   ├── 🐍 coordinate_system.py
│       │   │   ├── 🐍 curve.py
│       │   │   ├── 🐍 layout.py
│       │   │   ├── 🐍 renderer.py
│       │   │   └── 🐍 scaling.py
│       │   └── 🐍 __init__.py
│       ├── 🐍 __init__.py
│       └── 🐍 main.py
├── 📁 tests
│   ├── 📁 core
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 test_configuration.py
│   ├── 📁 simulation
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 test_events.py
│   │   ├── 🐍 test_history.py
│   │   ├── 🐍 test_simulator.py
│   │   └── 🐍 test_state.py
│   ├── 📁 topics
│   │   ├── 📁 asymptotic
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 test_complexity.py
│   │   │   ├── 🐍 test_model.py
│   │   │   └── 🐍 test_visualizer.py
│   │   ├── 📁 bst
│   │   │   ├── 🐍 test_bst_model.py
│   │   │   ├── 🐍 test_bst_operations.py
│   │   │   └── 🐍 test_bst_simulation.py
│   │   ├── 📁 heap
│   │   │   ├── 🐍 test_heap_model.py
│   │   │   ├── 🐍 test_heap_operations.py
│   │   │   └── 🐍 test_heap_simulation.py
│   │   ├── 📁 linked_list
│   │   │   ├── 🐍 test_linked_list_model.py
│   │   │   ├── 🐍 test_operations.py
│   │   │   └── 🐍 test_simulation.py
│   │   ├── 📁 queue
│   │   │   ├── 🐍 test_queue_model.py
│   │   │   ├── 🐍 test_queue_operations.py
│   │   │   └── 🐍 test_queue_simulation.py
│   │   ├── 📁 stack
│   │   │   ├── 🐍 test_stack_model.py
│   │   │   ├── 🐍 test_stack_operations.py
│   │   │   └── 🐍 test_stack_simulation.py
│   │   └── 🐍 __init__.py
│   ├── 📁 ui
│   │   ├── 📁 compontets
│   │   │   ├── 🐍 checkbox.py
│   │   │   └── 🐍 radio_button.py
│   │   ├── 📁 screens
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 test_asymptotic.py
│   │   │   ├── 🐍 test_main_menu.py
│   │   │   ├── 🐍 test_screen.py
│   │   │   └── 🐍 test_screen_manager.py
│   │   └── 🐍 __init__.py
│   ├── 📁 visualization
│   │   ├── 📁 graph
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 test_bounds.py
│   │   │   ├── 🐍 test_coordinate_system.py
│   │   │   ├── 🐍 test_curve.py
│   │   │   ├── 🐍 test_layout.py
│   │   │   ├── 🐍 test_renderer.py
│   │   │   └── 🐍 test_scaling.py
│   │   └── 🐍 __init__.py
│   └── 🐍 __init__.py
├── ⚖️ LICENSE
├── ⚙️ pyproject.toml
├── 📘 README.md
├── 📝 requirements.txt
└── 🐍 smoke_test.py
```
each topic follows the same pattern of `model.py` companied by `operations.py` and `simulation.py`.
## Architecture notes

- **`Screen`** is the shared base class every topic screen extends. It provides the back button, the Slow/Normal/Fast speed control, and `cancel_current_simulation()` for editing actions that should override an in-progress animation rather than being silently refused.
- Simulations are built by copying the model's current state, stepping through the operation, and recording each intermediate state as an immutable snapshot. Nothing is applied to the real model until the simulation reaches its end and calls `commit()`.
- Randomize buttons bypass the animation layer entirely: they mutate the model directly through its real methods (`push`, `enqueue`, `insert`, `build_heap`, etc.) for an instant result, the same way the Sorting screen's Randomize always has.

## Known limitations

- BST's Randomize draws values in random order, so a worst-case shuffle can produce a skewed (deep) tree rather than a balanced one.
- Switching a Heap between Min and Max rebuilds the heap from scratch, so a randomized heap does not survive a heap-type toggle.
- Hash Table capacity does not auto-resize; filling an open-addressing table raises a clear error instead of silently growing.