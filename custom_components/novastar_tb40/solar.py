"""Brightness policy shared by the startup and periodic updates."""

START_ELEVATION = 5.5
END_ELEVATION = -3.5
MIN_BRIGHTNESS = 8.0
RETRY_TIMES = (5, 10, 20, 30)


def solar_target(elevation):
    """Return the brightness for the given solar elevation."""
    progress = (START_ELEVATION - elevation) / (START_ELEVATION - END_ELEVATION)
    progress = max(0, min(1, progress))
    return round(100 - progress * (100 - MIN_BRIGHTNESS), 1)


def solar_step(elevation, current):
    """Dim gradually and preserve a lower manual setting."""
    target = solar_target(elevation)
    if target >= current:
        return None
    limit = 0.4 if min(current, target) <= 15 else 1.5
    proposed = round(max(target, current - limit), 1)
    return proposed if round(current - proposed, 1) >= 0.3 else None
