class BoundsCalculator:
    """Calculates bounds for generated graph curves."""

    def calculate_y_bounds(
        self,
        curves: list[list[tuple[float, float]]],
    ) -> tuple[float, float]:
        """Return the minimum and maximum Y values across all curves."""

        if not curves:
            raise ValueError("At least one curve is required.")

        points = [
            point
            for curve in curves
            for point in curve
        ]

        if not points:
            raise ValueError("Curves must contain at least one point.")

        y_values = [y for _, y in points]

        return min(y_values), max(y_values)