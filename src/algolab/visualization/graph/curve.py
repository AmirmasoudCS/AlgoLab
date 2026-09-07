class CurveGenerator:
    """Generates points for a mathematical function."""

    def generate(
        self,
        function,
        minimum: float,
        maximum: float,
        samples: int = 100,
    ) -> list[tuple[float, float]]:
        """Generate evenly spaced points for a mathematical function."""

        if samples < 2:
            raise ValueError("Samples must be at least 2.")

        if maximum <= minimum:
            raise ValueError("Maximum must be greater than minimum.")

        step = (maximum - minimum) / (samples - 1)

        return [
            (
                minimum + index * step,
                function(minimum + index * step),
            )
            for index in range(samples)
        ]