# AlgoLab

A desktop application built with Python and Pygame for visualizing data structures and algorithms.

Each operation is presented as a **step-by-step**, **pausable**, **rewindable** animation, with a live explanation of what is happening. AlgoLab was developed as an educational companion for a Data Structures and Algorithms course.

## 📚 Topics

* **Asymptotic Notation**: Complexity graphs with adjustable inputs
* **Linked Lists**: Insert, delete, search
* **Stacks**: Push, pop, peek
* **Queues**: Enqueue, dequeue, peek
* **Binary Search Trees**: Insert, search, delete, min/max, traversals
* **Heaps**: Min/Max heaps, insert, peek, extract, heapify
* **Graphs**: Directed/undirected, weighted/unweighted, BFS, DFS, Dijkstra, Bellman-Ford
* **Sorting**: Bubble Sort, Insertion Sort, Merge Sort, Quick Sort, Heap Sort
* **Hash Tables & Sets**: Chaining, probing, double hashing, Set/Map modes, configurable hash functions, collision counting

## ✨ Features

* Step-by-step, pausable, and rewindable simulations
* Adjustable animation speed
* Live explanations of operations
* Color-coded operations and legends
* Configurable data structure attributes
* Randomize button for every topic
* Keyboard shortcuts:

  * `P` Pause/Resume
  * `<-` / `->` Step backward/forward
  * `Enter` Run the primary action

## ⚙️ Getting Started

### Requirements

* Python 3.10+
* Pygame

### 1. Clone the Repository

```bash
git clone https://github.com/AmirmasoudCS/AlgoLab.git
cd AlgoLab
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

* **Windows:**

```bash
.venv\Scripts\activate
```

* **Linux / MacOS:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

* **Run from the source:**

```bash
python -m algolab.main
```

* **Build a standalone application:**
AlgoLab can also be packaged as a standalone executable using Pyinstaller.
```bash
pyinstaller AlgoLab.spec
```
The packages application will be available in the `dist/` directory.

## 🏗️ Architecture

Each topic follows the same structure:

```text
model.py       # Data structure and state
operations.py  # Operations performed on the structure
simulation.py  # Step-by-step simulation
```

Simulations operate on a copy of the model's state and record each intermediate state as an immutable snapshot. The real model is only updated when the simulation completes.

This allows operations to be **paused**, **replayed**, **rewound**, and **committed** without modifying the actual data structure during the animation.

Randomize actions bypass the simulation layer and use the data structure's normal operations to produce an immediate state.

## 📁 Project Structure

```text
📁 AlgoLab
├── 📁 assets
│   ├── 📄 icon.ico
│   └── 🖼️ icon.png
├── 📁 config
│   └── ⚙️ config.toml
├── 📁 log
│
├── 📁 src
│   └── 📁 algolab
│       ├── 📁 core
│       ├── 📁 simulation
│       ├── 📁 topics
│       │   ├── 📁 asymptotic
│       │   ├── 📁 bst
│       │   ├── 📁 graph
│       │   ├── 📁 hash_table
│       │   ├── 📁 heap
│       │   ├── 📁 linked_list
│       │   ├── 📁 queue
│       │   ├── 📁 sorting
│       │   └── 📁 stack
│       ├── 📁 ui
│       │   ├── 📁 components
│       │   └── 📁 screens
│       ├── 📁 visualization
│       │   └── 📁 graph
│       └── 🐍 main.py
│
├── 📁 tests
│   ├── 📁 core
│   ├── 📁 simulation
│   ├── 📁 topics
│   ├── 📁 ui
│   └── 📁 visualization
│
├── ⚖️ LICENSE
├── ⚙️ pyproject.toml
├── 📘 README.md
├── 📝 requirements.txt
└── 🐍 smoke_test.py
```

## 🧪 Testing

AlgoLab uses `pytest` for automated testing.

```bash
pytest
```

Tests cover the core logic, simulation system, data structure operations, UI components, and visualization utilities.

## ⚠️ Known Limitations

* **BST Randomization** can produce highly skewed trees depending on insertion order.
* **Heap Type Switching** rebuilds the heap when switching between Min and Max modes.
* **Hash Tables** do not automatically resize when an open-addressing table becomes full.

## ⚖️ License

This project is licensed under the MIT License.
