from itertools import permutations
from typing import List, Union
import logging

from nltk.corpus import words


class Solution:
    _guessed = set()
    _full_words = set([
        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
        "A", "S", "D", "F", "G", "H", "J", "K", "L", "Z",
        "X", "C", "V", "B", "N", "M",
    ])
    _dict = set(words.words())
    _clue = set()
    _answer = ["", "", "", "", ""]

    def __init__(self):
        pass

    @property
    def guessed(self):
        return self._guessed

    @property
    def full_words(self):
        return self._full_words

    @property
    def remain(self):
        return self.full_words - self.guessed

    @property
    def dictionary(self):
        return self._dict

    @property
    def clue(self):
        return self._clue

    @property
    def answer(self):
        return self._answer

    @property
    def answer_len(self):
        return len(list(filter(lambda x: x != "", self.answer)))

    def guess_word(self, char: str):
        """Add impossible word."""
        if len(char) != 1:
            raise ValueError("guess word must be length 1")
        elif char in self.clue:
            print(f"{char} is in clue")
            return None
        char = char.upper()
        self.guessed.add(char)
        logging.debug(f"new guessed word: {char}")

    def add_clue(self, char: str, pos: Union[int, bool] = False):
        """Add words that must appear."""
        char = char.upper()
        if len(char) != 1:
            raise ValueError("clue must be length 1")
        elif char in self.guessed:
            print(f"{char} is in the guessed word")
            return None

        if pos is not False:
            self.answer[pos] = char
            logging.debug(f"clue: {char} added to pos: {pos}")
        self.clue.add(char)
        logging.debug(f"clue: {char} added without pos")

    def check_word(self, word: str, check_dict: bool):
        """Check if word is feasible."""
        if check_dict and (word.lower() not in self.dictionary):
            # logging.debug(f"{word} did not pass dict check")
            return False

        elif not self.clue.issubset(set(list(word.upper()))):
            # if clue is not a subset of the word
            logging.debug(f"{word} did not pass clue check")
            return False

        logging.debug(f"{word} passed clue and dict check")
        return True

    def form_word(self, chars: List[str]):
        """Form words with the chars."""
        word = ""
        char_index = 0

        for index in range(5):
            if self.answer[index] != "":
                word += self.answer[index]
            else:
                word += chars[char_index]
                char_index += 1

        return word.upper()

    def list_words(self, check_dict: bool):
        """List possible words."""
        num = 5 - self.answer_len
        perm = permutations(self.remain, num)
        perm = list(perm)

        logging.debug(f"Total permutations: {len(perm)}")

        for chars in perm:
            word = self.form_word(chars)
            if self.check_word(word, check_dict):
                print(word.lower())


def main():
    """Playing game"""

    logging.basicConfig(level=logging.INFO)

    actions = {
        "quit": 0,
        "list_word": 1,
        "add_clue": 2,
        "remove_word": 3,
        "check_clue": 4,
        "remain_word": 5,
        "current_answer": 6,
        "restart": 7
    }

    run_flag = True
    while(run_flag):
        print(f"Allowed actions: {list(actions.keys())}")
        action_str = input("What do you want to do? ")
        try:
            sol = Solution()
            action = actions[action_str]
            if action == 0:
                run_flag = False
            elif action == 1:
                check_dict_flag = True
                check_dict = input("check dictionary? ")
                if check_dict.lower() in ["false", "no"]:
                    check_dict_flag = False
                sol.list_words(check_dict=check_dict_flag)
            elif action == 2:
                clues = input("What is the word you guessed? ")
                pos = input("do you know the position? ")
                if pos.lower() in ["yes"]:
                    for clue in clues:
                        position = input(f"what is the position for {clue} ")
                        position = int(position)
                        sol.add_clue(clue, pos=position)
                        print(f"Current clue: {sol.clue}")
                else:
                    for clue in clues:
                        sol.add_clue(clue)
                        print(f"Current clue: {sol.clue}")
            elif action == 3:
                words = input("What are the impossible chars? ")
                for word in words:
                    sol.guess_word(word)
                print(f"Remaining words: {sol.remain}")
            elif action == 4:
                print(f"Current clue: {sol.clue}")
            elif action == 5:
                print(f"Remaining words: {sol.remain}")
            elif action == 6:
                print(f"Current answer: {sol.answer}")
            elif action == 7:
                del sol
                sol = Solution()
                print("Restarted")
            else:
                raise KeyError
        except KeyError:
            print(f"Allowed actions: {list(actions.keys())}")


if __name__ == "__main__":
    main()
