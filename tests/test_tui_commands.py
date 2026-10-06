from __future__ import annotations

import unittest

from zeta_coding.tui.app import _command_message_uses_transcript


class CommandOutputRoutingTests(unittest.TestCase):
    def test_models_output_is_rendered_in_transcript(self) -> None:
        self.assertTrue(_command_message_uses_transcript("/models"))

    def test_modal_commands_remain_modal(self) -> None:
        self.assertFalse(_command_message_uses_transcript("/help"))
        self.assertFalse(_command_message_uses_transcript("/status"))


if __name__ == "__main__":
    unittest.main()
