"""Tests for the AVL tree model and its step-by-step simulator."""

from __future__ import annotations

import random
import re
from collections import Counter

import pytest

from algolab.topics.avl.model import AVLNode, AVLTree
from algolab.topics.avl.simulation import (
    AVLNodeState,
    AVLSimulationState,
    AVLSimulator,
)


def _model_shape(node):
    if node is None:
        return None

    return (
        node.value,
        node.height,
        _model_shape(node.left),
        _model_shape(node.right),
    )


def _snapshot_shape(data):
    nodes = {node.node_id: node for node in data.nodes}

    def build(node_id):
        if node_id is None:
            return None

        node = nodes[node_id]

        return (
            node.value,
            node.height,
            build(node.left_id),
            build(node.right_id),
        )

    return build(data.root_id)


def _check_snapshot(data, allow_duplicate_value):
    """Every simulation frame must be a well-formed BST snapshot."""

    nodes = {node.node_id: node for node in data.nodes}

    assert len(nodes) == len(data.nodes)

    if data.root_id is None:
        assert not nodes
        return

    seen: set[int] = set()
    order: list[object] = []

    def walk(node_id):
        assert node_id not in seen
        seen.add(node_id)
        node = nodes[node_id]

        if node.left_id is not None:
            walk(node.left_id)

        order.append(node.value)

        if node.right_id is not None:
            walk(node.right_id)

    walk(data.root_id)

    assert seen == set(nodes)

    for left, right in zip(order, order[1:]):
        assert left <= right if allow_duplicate_value else left < right

    for node in nodes.values():
        left = nodes[node.left_id].height if node.left_id is not None else 0
        right = nodes[node.right_id].height if node.right_id is not None else 0
        assert node.balance == left - right

    for name in (
        "active_node_id",
        "result_node_id",
        "unbalanced_node_id",
    ):
        value = getattr(data, name)
        assert value is None or value in nodes

    for node_id in data.rotation_node_ids:
        assert node_id in nodes


# ----------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------


def test_random_operations_keep_avl_invariant():
    rng = random.Random(1)

    for _ in range(150):
        tree: AVLTree = AVLTree()
        reference: set[int] = set()
        high = rng.choice([15, 40, 200])

        for _ in range(rng.randint(20, 120)):
            value = rng.randint(1, high)

            if rng.random() < 0.55:
                if value in reference:
                    before = tree.in_order()

                    with pytest.raises(ValueError):
                        tree.insert(value)

                    assert tree.in_order() == before
                else:
                    node = tree.insert(value)
                    assert isinstance(node, AVLNode)
                    assert node.value == value
                    reference.add(value)
            else:
                deleted = tree.delete(value)

                if value in reference:
                    assert deleted == value
                    reference.remove(value)
                else:
                    assert deleted is None

            assert tree.in_order() == sorted(reference)
            assert tree.size == len(reference)
            assert tree.is_balanced()


def test_sorted_inserts_stay_logarithmic():
    tree: AVLTree = AVLTree()

    for value in range(1, 1024):
        tree.insert(value)

    assert tree.root.height == 10


@pytest.mark.parametrize(
    "sequence",
    [[10, 20, 30], [30, 20, 10], [30, 10, 20], [10, 30, 20]],
)
def test_each_rotation_case_produces_the_same_balanced_tree(sequence):
    tree: AVLTree = AVLTree()

    for value in sequence:
        tree.insert(value)

    assert tree.root.value == 20
    assert tree.root.left.value == 10
    assert tree.root.right.value == 30


# ----------------------------------------------------------------------
# Simulator
# ----------------------------------------------------------------------


def test_simulation_frames_are_valid_and_match_the_committed_model():
    rng = random.Random(7)
    cases: Counter[str] = Counter()

    for _ in range(200):
        tree: AVLTree = AVLTree()
        simulator = AVLSimulator(tree)
        reference: set[int] = set()
        high = rng.choice([12, 30, 90])

        for _ in range(rng.randint(10, 60)):
            value = rng.randint(1, high)
            is_insert = rng.random() < 0.58

            simulation = (
                simulator.insert(value)
                if is_insert
                else simulator.delete(value)
            )
            states = simulation.states

            assert [s.step for s in states] == list(range(len(states)))

            # The value-replace frame of a two-children delete holds
            # the successor's value twice, briefly.
            two_children = any(
                "two children" in s.data.description for s in states
            )

            for state in states:
                assert isinstance(state.data, AVLSimulationState)
                _check_snapshot(state.data, allow_duplicate_value=two_children)

                match = re.search(
                    r"this is the (\w+-\w+) case", state.data.description
                )

                if match:
                    cases[match.group(1)] += 1

            rotated = any(s.data.rotation_node_ids for s in states)
            flagged = any(
                s.data.unbalanced_node_id is not None for s in states
            )
            assert rotated == flagged

            before = _model_shape(tree.root)
            simulation.commit(tree)

            if is_insert:
                reference.add(value)
            else:
                reference.discard(value)

            assert tree.is_balanced()
            assert tree.in_order() == sorted(reference)
            assert _snapshot_shape(states[-1].data) == _model_shape(tree.root)

            if not simulation.should_commit:
                assert before == _model_shape(tree.root)

    assert set(cases) == {"Left-Left", "Left-Right", "Right-Right", "Right-Left"}


def test_inherited_simulations_carry_avl_data():
    tree: AVLTree = AVLTree()
    simulator = AVLSimulator(tree)

    for value in [50, 30, 70, 20, 40, 60, 80, 10]:
        simulator.insert(value).commit(tree)

    simulation = simulator.find_min()
    data = simulation.states[-1].data
    result = {n.node_id: n for n in data.nodes}[data.result_node_id]

    assert result.value == 10
    assert isinstance(result, AVLNodeState)

    traversal = simulator.in_order()

    assert list(traversal.states[-1].data.traversal_values) == tree.in_order()


def test_empty_tree_edge_cases():
    simulator = AVLSimulator(AVLTree())

    assert simulator.insert(5).states[-1].data.nodes[0].value == 5
    assert not simulator.delete(5).should_commit