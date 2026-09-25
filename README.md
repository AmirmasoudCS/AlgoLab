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

### Installation

```bash
git clone https://github.com/AmirmasoudCS/AlgoLab.git
cd AlgoLab

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Run the application:

```bash
python -m algolab.main
```

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
