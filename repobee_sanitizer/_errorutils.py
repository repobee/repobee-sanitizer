from typing import Optional

import repobee_plug as plug


class SanitizeError(plug.PlugError):
    def __init__(self, msg: str, cause: Optional[Exception] = None):
        self.msg = msg
        super().__init__(msg, cause)
