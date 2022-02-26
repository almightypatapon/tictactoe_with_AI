from random import choice


class Field:
    coordinates = {1: {3: 0, 2: 3, 1: 6}, 2: {3: 1, 2: 4, 1: 7}, 3: {3: 2, 2: 5, 1: 8}}

    def __init__(self, field=None):
        if field is None:
            self.field = [*range(0, 9)]
        else:
            self.field = [symbol if symbol != '_' else i for i, symbol in enumerate(field)]

    def __str__(self):
        masked_field = [' ' if isinstance(symbol, int) else symbol for symbol in self.field]
        return('---------\n' +
               '| {} |\n'.format(' '.join(masked_field[:3])) +
               '| {} |\n'.format(' '.join(masked_field[3:6])) +
               '| {} |\n'.format(' '.join(masked_field[6:9])) +
               '---------')

    def vectors(self):
        columns = [self.field[::3], self.field[1::3], self.field[2::3]]
        rows = [self.field[:3], self.field[3:6], self.field[6:]]
        diagonals = [self.field[::4], self.field[2:7:2]]
        return columns + rows + diagonals

    def next_symbol(self):
        return 'X' if self.field.count('X') == self.field.count('O') else 'O'

    def pairs(self, symbol):
        return [vector for vector in self.vectors() if vector.count(symbol) == 2 and any(isinstance(symbol, int) for symbol in vector)]

    def empty_indices(self):
        return [index for index in self.field if isinstance(index, int)]

    def winning(self, player):
        return True if 3 * [player] in self.vectors() else False


class Player:
    def __init__(self, field_cls):
        self.field_cls = field_cls

    def next_move(self):
        while True:
            user_input = input('Enter the coordinates: ')
            i, j = user_input.split() if user_input.count(' ') == 1 else [' ', ' ']
            if not i.isdigit() or not j.isdigit():
                print('You should enter numbers!')
            elif not 0 < int(i) < 4 or not 0 < int(j) < 4:
                print('Coordinates should be from 1 to 3!')
            elif isinstance(self.field_cls.field[self.field_cls.coordinates[int(i)][int(j)]], str):
                print('This cell is occupied! Choose another one!')
            else:
                self.field_cls.field[self.field_cls.coordinates[int(i)][int(j)]] = self.field_cls.next_symbol()
                break


class EasyBot(Player):

    def random_move(self):
        self.field_cls.field[choice([i for i, x in enumerate(self.field_cls.field) if isinstance(x, int)])] = self.field_cls.next_symbol()

    def next_move(self):
        print('Making move level "easy"')
        return self.random_move()


class MediumBot(EasyBot):

    def win_def_move(self, symbol):
        self.field_cls.field[[x for x in self.field_cls.pairs(symbol)[0] if isinstance(x, int)][0]] = self.field_cls.next_symbol()

    def next_move(self):
        opponent_symbol = 'X' if 'X' != self.field_cls.next_symbol() else 'O'
        print('Making move level "medium"')
        return self.win_def_move(self.field_cls.next_symbol()) if self.field_cls.pairs(self.field_cls.next_symbol()) \
            else self.win_def_move(opponent_symbol) if self.field_cls.pairs(opponent_symbol) else self.random_move()


class HardBot(MediumBot):

    def __init__(self, field_cls):
        super().__init__(field_cls)
        self.player_symbol = self.field_cls.next_symbol()
        self.opponent_symbol = 'X' if 'X' != self.field_cls.next_symbol() else 'O'

    def minimax(self, field_cls, player):

        avail_spots = field_cls.empty_indices()

        if field_cls.winning(self.opponent_symbol):
            return {'score': -10}
        elif field_cls.winning(self.player_symbol):
            return {'score': 10}
        elif len(avail_spots) == 0:
            return {'score': 0}
        else:
            moves = []

            for i in avail_spots:
                move = {'index': i}
                field_cls.field[i] = player

                if player == self.player_symbol:
                    result = self.minimax(field_cls, self.opponent_symbol)
                    move.update({'score': result['score']})
                else:
                    result = self.minimax(field_cls, self.player_symbol)
                    move.update({'score': result['score']})

                field_cls.field[i] = move['index']
                moves.append(move)

            if player == self.player_symbol:
                best_score = -100
                for move in moves:
                    if move['score'] > best_score:
                        best_score = move['score']
                        best_move = move
            else:
                best_score = 100
                for move in moves:
                    if move['score'] < best_score:
                        best_score = move['score']
                        best_move = move
        return best_move

    def minimax_move(self):
        self.field_cls.field[self.minimax(self.field_cls, self.field_cls.next_symbol())['index']] = self.field_cls.next_symbol()

    def next_move(self):
        print('Making move level "hard"')
        return self.minimax_move()


class WhoPlays:
    def __init__(self, field_cls, player1, player2):
        self.player1 = Player(field_cls) if player1 == 'user' else EasyBot(field_cls) if player1 == 'easy' else MediumBot(field_cls) if player1 == 'medium' else HardBot(field_cls)
        self.player2 = Player(field_cls) if player2 == 'user' else EasyBot(field_cls) if player2 == 'easy' else MediumBot(field_cls) if player2 == 'medium' else HardBot(field_cls)


def play():

    while True:
        command = input('Input command: ')
        if command == 'exit':
            break
        elif command.count(' ') == 2 and all(x == 'start' if i == 0 else x in ['user', 'easy', 'medium', 'hard'] for i, x in enumerate(command.split())):
            field = Field()
            players = WhoPlays(field, command.split()[1], command.split()[2])
            print(field)
            i = 1
            while True:
                players.player1.next_move() if i % 2 != 0 else players.player2.next_move()
                print(field)
                if field.winning('X'):
                    print('X wins')
                    break
                elif field.winning('O'):
                    print('O wins')
                    break
                elif not field.empty_indices():
                    print('Draw')
                    break
                else:
                    i += 1
        else:
            print('Bad parameters')


play()
