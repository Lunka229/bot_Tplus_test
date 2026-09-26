from collections import defaultdict


class ConversationManager:
    def __init__(self, max_messages: int = 10) -> None:
        self.max_messages = max_messages
        self._histories: dict[
            int,
            list[dict[str, str]],
        ] = defaultdict(list)

    def add_user_message(
        self,
        user_id: int,
        content: str,
    ) -> None:
        self._histories[user_id].append(
            {
                "role": "user",
                "content": content,
            }
        )

        self._trim_history(user_id)

    def add_assistant_message(
        self,
        user_id: int,
        content: str,
    ) -> None:
        self._histories[user_id].append(
            {
                "role": "assistant",
                "content": content,
            }
        )

        self._trim_history(user_id)

    def get_history(
        self,
        user_id: int,
    ) -> list[dict[str, str]]:
        return list(self._histories[user_id])

    def clear(self, user_id: int) -> None:
        self._histories.pop(user_id, None)

    def _trim_history(self, user_id: int) -> None:
        history = self._histories[user_id]

        if len(history) > self.max_messages:
            self._histories[user_id] = history[
                -self.max_messages:
            ]