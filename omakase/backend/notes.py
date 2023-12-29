"""
Query and edit decks
"""


class ManipulateDecks:
    def __init__(self, om_username: str) -> None:
        """Manipulate decks of `om_username`"""
        self._om_username = om_username

    def list_decks(self) -> list[str]:
        """List decks for a given omakase user

        Args:
            om_username: name of the omakase user

        Returns:
            List of decks
        """
        return self._list_decks_mock()

    def _list_decks_mock(self) -> list[str]:
        # TODO: implement
        if self._om_username == "X":
            decks = ["deck1", "deck2"]
        else:
            decks = []
        return decks
