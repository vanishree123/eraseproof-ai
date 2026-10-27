def normalize_identifier(value: str) -> str:
    """Normalize identifiers for exact matching."""
    return value.strip().casefold()


def find_identifier_matches(
    target_identifiers: dict[str, list[str]],
    records: list[dict],
) -> list[dict]:
    """
    Find records sharing an identifier of the same type.
    This function only finds candidates; it never deletes data.
    """
    target_pairs = {
        (kind, normalize_identifier(value))
        for kind, values in target_identifiers.items()
        for value in values
        if value.strip()
    }

    matches = []

    for record in records:
        record_identifiers = record.get("identifiers", {})
        matched_on = []

        for kind, values in record_identifiers.items():
            if isinstance(values, str):
                values = [values]

            for value in values:
                if not isinstance(value, str) or not value.strip():
                    continue

                pair = (kind, normalize_identifier(value))

                if pair in target_pairs:
                    matched_on.append({
                        "type": kind,
                        "value": value,
                    })

        if matched_on:
            matches.append({
                **record,
                "matched_on": matched_on,
            })

    return matches