# AlgoLab

A desktop application built with Python and Pygame for visualizing data structures and algorithms.

Each operation is presented as a **step-by-step**, **pausable**, **rewindable** animation, with a live explanation of what is happening. AlgoLab was developed as an educational companion for a Data Structures and Algorithms course.

## 📸 Screenshots

<div align="center">

<img src="screenshots/main_menu.png" width="800"/>

**Main Menu** — pick any of the nine topics to open its dedicated visualizer.

</div>

<div align="center">

<img src="screenshots/stack.png" width="800"/>

**Stack** — push, pop, and peek animated step by step, with a live TOP pointer.

</div>

<div align="center">

<img src="screenshots/queue.png" width="800"/>

**Queue** — enqueue and dequeue animated with FRONT and REAR pointers.

</div>

<div align="center">

<img src="screenshots/linked_list.png" width="800"/>

**Linked List** — insert and delete operations, with HEAD and the algorithm's temporary PREVIOUS / CURRENT / NEW pointers shown as they move.

</div>

<div align="center">

<img src="screenshots/bst.png" width="800"/>

**Binary Search Tree** — insert, search, delete, and traversals, rendered as a live tree diagram.

</div>

<div align="center">

<img src="screenshots/heap.png" width="800"/>

**Heap** — Min/Max heap operations shown as both a tree and its underlying array, side by side.

</div>

<div align="center">

<img src="screenshots/graph.png" width="800"/>

**Graph** — build a custom directed/undirected, weighted/unweighted graph and run BFS, DFS, Dijkstra, or Bellman-Ford on it.

</div>

<div align="center">

<img src="screenshots/merge_sort.png" width="800"/>

**Sorting** — Merge Sort visualized as an animated bar chart (Bubble, Selection, Insertion, Quick, and Heap Sort are also available on the same screen).

</div>

<div align="center">

<img src="screenshots/hash_chaing.png" width="800"/>

**Hash Table** — separate chaining collision resolution with a live load factor bar (linear probing, quadratic probing, and double hashing are also supported).

</div>

<div align="center">

<img src="screenshots/asymptotic.png" width="800"/>

**Asymptotic Notation** — compare Big-O growth curves from O(1) to O(n^n) with an adjustable input size.

</div>

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
* Per-topic Big-O reference table (Info button on every topic screen)
* Fullscreen, auto-scaled to the machine's native resolution
* Screenshot capture (`F12`), saved to `assets/screenshots/`
* Keyboard shortcuts:

  * `P` Pause/Resume
  * `<-` / `->` Step backward/forward
  * `Enter` Run the primary action
  * `F12` Take a screenshot
  * `Esc` Quit

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
│   ├── 🖼️ icon.png
│   └── 📁 screenshots      # F12 auto-captures land here (gitignored)
├── 📁 screenshots          # curated images used in this README
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
* **Queue's `dequeue`** is O(n) in this implementation (`list.pop(0)`), not the textbook O(1) — a deque- or linked-list-backed queue would achieve O(1).

## ⚖️ License

This project is licensed under the MIT License.