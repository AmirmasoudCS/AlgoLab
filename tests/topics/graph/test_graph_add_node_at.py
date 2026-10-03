from algolab.topics.graph.model import GraphModel


def test_places_a_pinned_node_exactly_where_asked():
    graph = GraphModel()

    node_id = graph.add_node_at(123.5, 456.25, "Q")
    node = graph.get_node(node_id)

    assert (node.node_id, node.label, node.x, node.y, node.pinned) == (
        node_id, "Q", 123.5, 456.25, True
    )


def test_label_defaults_to_the_id_and_ids_keep_counting():
    graph = GraphModel()

    first = graph.add_node_at(10, 10)
    second = graph.add_node()
    third = graph.add_node_at(20, 20)

    assert (first, second, third) == (0, 1, 2)
    assert graph.get_node(first).label == "0"


def test_unlike_add_node_it_never_moves_the_other_nodes():
    graph = GraphModel()

    for _ in range(4):
        graph.add_node()

    graph.recompute_layout(640, 500, 200)
    before = {n.node_id: (n.x, n.y, n.pinned) for n in graph.nodes}

    graph.add_node_at(900, 700)

    after = {n.node_id: (n.x, n.y, n.pinned) for n in graph.nodes if n.node_id in before}

    assert after == before


def test_add_node_would_have_moved_them():
    # Documents why add_node_at exists: add_node re-spaces unpinned nodes.
    graph = GraphModel()
    graph.add_node()
    graph.recompute_layout(640, 500, 200)
    before = (graph.nodes[0].x, graph.nodes[0].y)

    graph.add_node()

    assert (graph.nodes[0].x, graph.nodes[0].y) != before


def test_hand_placed_nodes_survive_a_save_and_load_and_layout_changes():
    graph = GraphModel(directed=True)
    a = graph.add_node_at(300, 300, "A")
    b = graph.add_node_at(700, 300, "B")
    graph.add_edge(a, b, 2)

    restored = GraphModel.from_dict(graph.to_dict())
    restored.recompute_layout(640, 500, 200)               # must not touch pinned nodes

    assert [(n.x, n.y, n.pinned) for n in restored.nodes] == [(300.0, 300.0, True), (700.0, 300.0, True)]
    assert restored.add_node_at(1, 1) == 2


def test_works_alongside_removal():
    graph = GraphModel()
    a = graph.add_node_at(300, 300, "A")
    b = graph.add_node_at(700, 300, "B")
    graph.add_edge(a, b)

    graph.remove_node(a)

    assert [n.label for n in graph.nodes] == ["B"] and graph.edges == []
    assert graph.add_node_at(5, 5) == 2, "ids are never reused"