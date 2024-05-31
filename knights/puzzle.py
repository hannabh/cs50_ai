from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Information about the game:
    # each character can be a knight or knave, but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # Information from what characters say:
    Biconditional(AKnight, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Information about the game:
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    # Information from what characters say:
    Biconditional(AKnight, And(AKnave, BKnave)),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Information about the game:
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    # Information from what characters say:
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # Information about the game:
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),
    # Information from what characters say:
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Or(
        # A says "I am a knight"
        And(
            Or(
                And(AKnight, AKnight),  # statement 1 true
                And(AKnave, Not(AKnight))  # statement 1 false
            ),
            # B says "A said 'I am a knave'."
            BKnave
        ),
        # A says "I am a knave"
        And(
            Or(
                And(AKnight, AKnave),  # statement 1 true
                And(AKnave, Not(AKnave))  # statement 1 false
            ),
            # B says "A said 'I am a knave'."
            BKnight
        )
    ),
    # B says "C is a knave."
    Biconditional(BKnight, CKnave),
    # C says "A is a knight."
    Biconditional(CKnight, AKnight),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()