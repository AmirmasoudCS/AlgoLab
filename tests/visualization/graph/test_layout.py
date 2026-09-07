from algolab.visualization.graph.layout import GraphLayout


def test_graph_layout_stores_values():
    layout = GraphLayout(
        x=100,
        y=50,
        width=800,
        height=500,
    )

    assert layout.x == 100
    assert layout.y == 50
    assert layout.width == 800
    assert layout.height == 500


def test_graph_layout_is_immutable():
    layout = GraphLayout(
        x=100,
        y=50,
        width=800,
        height=500,
    )

    try:
        layout.x = 200
        assert False
    except AttributeError:
        pass