import itertools
import random


class Minesweeper():
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


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safe = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            self.mines.add(i for i in self.cells)
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if len(self.cells) == 0:
            self.safe.add(i for i in self.cells)
        return self.safe

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            mine = self.cells.remove(cell)
            self.count -= 1
            self.mines.add(mine)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            safe = self.cells.remove(cell)
            self.safe.add(safe)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        #Set the list of all potential moves
        self.potential_moves = [(i,j) for i in range(self.height) for j in range(self.width)]

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        #TEST--------------------------------TEST-----------------------------
        print(self.potential_moves)
        print(self.moves_made)
        print(self.safes)
        print(self.mines)

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)

        try:
            self.potential_moves.remove(cell)
        except:
            ("Element not in the list")

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
        self.moves_made.add(cell) # mark the cell as a move that has been made
        self.mark_safe(cell)    # mark the cell as safe

        #updating any sentence containing the cell
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)

        # add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        cells = set()
        
        
        x,y = cell
        

        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                temp = (i,j)
                if temp != cell and (temp not in self.moves_made and temp not in self.safes and temp not in self.mines ) :
                    cells.add(temp)
        new_sentence = Sentence(cells,count)
        self.knowledge.append(new_sentence)

        # mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base        

        for sentence in self.knowledge:
            if sentence.cells.issubset(new_sentence.cells):
                new_cells = new_sentence.cells - sentence.cells
                safe_cells = new_sentence.cells.intersection(sentence.cells) 
                new_count = new_sentence.count - sentence.count
                self.knowledge.append(Sentence(new_cells, new_count)) #add a new sentence with the substraction of the sets
                
                for i in safe_cells:
                    self.mark_safe(i)
                
                if len(new_cells) == new_count:
                    for i in new_cells:
                        self.mark_mine(i)


            elif new_sentence.cells.issubset(sentence.cells):
                new_cells = sentence.cells - new_sentence.cells
                new_count = sentence.count - new_sentence.count
                self.knowledge.append(Sentence(new_cells, new_count)) #add a new sentence with the substraction of the sets

                if len(new_cells) == new_count:
                    for i in new_cells:
                        self.mark_mine(i)



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                try:
                    self.potential_moves.remove(cell)
                except:
                    print("Element not in the list")
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        random_move = random.choice(self.potential_moves)
        self.potential_moves.remove(random_move)
        return random_move

