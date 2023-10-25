import string


class TextEqual:
    def __init__(self, original: str, alter_tokens=[]) -> None:
        """
        Creates the TextEqual Object
        :param original: the Original Text
        :param alter_tokens: tokens that will be ignored in altered text
        """
        self.original = original
        self.alter_tokens = alter_tokens

    def run(self, altered: str, ) -> tuple:
        """
        Checks textequality
        :param altered: the altered Text
        :return: bool
        """
        orig_altered = altered
        original = ''.join(
            char for char in self.original if char.isascii() or char in ['ä', 'ü', 'ö', 'Ä', 'Ü', 'Ö', 'ß'])
        altered = ' '.join(
            word for word in altered.split() if all(forbidden not in word for forbidden in self.alter_tokens))
        altered = ''.join(char for char in altered if char.isascii() or char in ['ä', 'ü', 'ö', 'Ä', 'Ü', 'Ö', 'ß'])
        original = ' '.join([word for word in original.split() if word in altered.split()])
        altered = altered.replace(' ', '')
        original = original.replace(' ', '')
        print(altered)
        print(original)
        if altered == original:
            return altered == original, orig_altered
        else:
            return altered == original, "FAILED"
