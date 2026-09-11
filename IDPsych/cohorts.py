"""Subject groups used in Wei, Mitchell & Maunsell (2023) and the stimulus
parameters that distinguish them. Subject IDs double as folder names."""

COHORTS = {
    "100ms": {
        "subjects": ["201", "203", "204", "205", "206"],
        "dotLifeMS": 100,
        "dotDensityDPD": 2.5,
        "note": "First group; subject 201 is shown with an open symbol in the paper",
    },
    "33ms": {
        "subjects": ["403", "404", "405", "406", "408"],
        "dotLifeMS": 33,
        "dotDensityDPD": 5,
        "note": "Main dataset (Fig 2)",
    },
    "control": {
        "subjects": ["603", "608"],
        "dotLifeMS": 33,
        "dotDensityDPD": 5,
        "note": "Increment-only sessions with baseline set to 50% minus each "
                "subject's decrement threshold; paired with subjects 403 and 408",
    },
}

# Symbol shown as open (white) in the paper's scatter plots
OPEN_SYMBOL = {"100ms": ["201"]}


def subjects(cohort):
    """Subject ID list for a cohort name ('100ms', '33ms', or 'control')."""
    return list(COHORTS[cohort]["subjects"])
