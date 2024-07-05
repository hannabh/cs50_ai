import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # loop over variables
        for var in self.domains.keys():
            # remove values from domain which don't have the same number of letters as the variable's length
            self.domains[var] = {x for x in self.domains[var] if len(x) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False

        overlap = self.crossword.overlaps[x, y] 
        # overlap is None if no overlap, or (i, j), where x's ith character overlaps y's jth character

        # if no overlap, x is already arc consistent with y
        if overlap == None:
            return revision
        else:
            # for each value in x's domain,
            # check if there is a corresponding value for y
            for x_word in self.domains[x].copy():
                consistent_val = False
                for y_word in self.domains[y]:
                    if x_word[overlap[0]] == y_word[overlap[1]]:
                        consistent_val = True
                        break
                # if no corresponding value for y, remove value from x's domain 
                if not consistent_val:
                    self.domains[x].remove(x_word)
                    revision = True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # TODO: bugfixes for this function

        if arcs == None:
            # begin with initial list of all arcs in the problem
            # each arc in arcs is a tuple (x, y) of a variable x and a different variable y
            vars = list(self.crossword.variables)
            arcs = []
            for i in range(len(vars)):
                for j in range(i+1, len(vars)):
                    arcs.append((vars[i], vars[j]))
        
        while len(arcs) != 0:
            # remove an arc from the queue
            x, y = arcs.pop(0)
            # enforce arc consistency
            if self.revise(x, y):
                # if all values are removed from a domain, constraint satisfaction not possible
                if len(self.domains[x]) == 0:
                    return False
                # else add additional arcs to queue to ensure still arc consistent
                else:
                    neighbours = self.crossword.neighbors(x)
                    neighbours.remove(y)
                    if neighbours:
                        for node in neighbours:
                            arcs.append((x, node))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # check all crossword variables are in the assignment
        return all(var in assignment.keys() for var in self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check all values are distinct
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        for var in assignment:
            # check every value is the correct length
            if var.length != len(assignment[var]):
                return False
            # check no conflicts between neighbouring variables
            neighbours = self.crossword.neighbors(var)
            for neighbour in neighbours:
                overlap = self.crossword.overlaps[var, neighbour]
                if overlap:
                    if neighbour in assignment:
                        if assignment[var][overlap[0]] != assignment[neighbour][overlap[1]]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain_values = list(self.domains[var])
        neighbours = self.crossword.neighbors(var)
        unassigned_neighbours = [x for x in neighbours if x not in assignment]

        vals_ruled_out = {val: 0 for val in domain_values}
        for val in domain_values:
            for neighbour in unassigned_neighbours:
                overlap = self.crossword.overlaps[var, neighbour]
                for neighbour_val in self.domains[neighbour]:
                    if val[overlap[0]] != neighbour_val[overlap[1]]:
                        vals_ruled_out[val] += 1

        domain_values.sort(key=lambda val: vals_ruled_out[val])
        return domain_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = [var for var in self.crossword.variables if var not in assignment]

        unassigned_variables.sort(key=lambda var: self.crossword.neighbors(var), reverse=True)
        unassigned_variables.sort(key=lambda var: len(self.domains[var]))
        return unassigned_variables[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
