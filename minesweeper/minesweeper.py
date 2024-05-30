import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # update the sentence so that cell is no longer in the sentence
            # but still represents a logically correct sentence given that cell is known to be a mine
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # update the sentence so that cell is no longer in the sentence
            # but still represents a logically correct sentence given that cell is known to be safe
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def nearby_cells(self, cell):
        """
        Returns a list of neighbouring cells on the board,
        excluding the cell itself
        """
        nearby_cells = []
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Check if cell is in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    nearby_cells.append((i, j))
        return nearby_cells

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`

        # self.cell = a safe move
        # self.count = number of neighbouring cells that have mines in them
        # indicate that count of the cell's neighbours are mines
        nearby_cells = self.nearby_cells(cell)
        sentence = Sentence(nearby_cells, count)
        # TODO: only include cells whose state is still undetermined in the sentence
        self.knowledge.append(sentence)

        # 4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            known_mines = (
                sentence.known_mines()
            )  # set of cells known to be mines based on sentence
            if known_mines:
                for cell in known_mines:
                    self.mark_mine(cell)
            known_safes = sentence.known_safes()
            if known_safes:
                for cell in known_safes:
                    self.mark_safe(cell)

        # 5) add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge
        sentence_pairs = itertools.combinations(self.knowledge, 2)
        for sentence1, sentence2 in sentence_pairs:
            # if we have 2 sentences set1 = count1 and set2 = count2, where set1 is a subset of set2,
            # we can construct a new sentence set2 - set1 = count2 - count1
            set1 = sentence1.cells
            set2 = sentence2.cells
            count1 = sentence1.count
            count2 = sentence2.count
            if set1.issubset(set2):
                new_sentence = Sentence(set2 - set1, count2 - count1)
                self.knowledge.append(new_sentence)

        # TODO: any time a change is made to self.knowledge, it may be possible to draw new inferences - add these!

    def available_moves(self):
        """
        Returns all possible moves (i, j) that haven't already been made
        """
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_moves.add((i, j))
        available_moves = {move for move in all_moves if move not in self.moves_made}
        return available_moves

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        available_moves = self.available_moves()
        for move in available_moves:
            if move in self.safes:
                return move
        # if no safe move guaranteed, return None
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_moves = self.available_moves()
        # moves that haven't already been made, and not known to be a mine
        moves = {move for move in available_moves if move not in self.mines}

        # if no such move possible, return None
        if len(moves) == 0:
            return None
        else:
            # choose randomly among moves
            return random.choice(list(moves))
