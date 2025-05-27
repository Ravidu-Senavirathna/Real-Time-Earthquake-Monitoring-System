def validate_earthquake(row):

    if row is None:
        return False

    if row["latitude"] is None:
        return False

    if row["longitude"] is None:
        return False

    if not (-90 <= row["latitude"] <= 90):
        return False

    if not (-180 <= row["longitude"] <= 180):
        return False

    if row["magnitude"] is None:
        return False

    return True