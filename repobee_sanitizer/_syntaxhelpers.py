import re
import repobee_plug as plug
from typing import List

START_BLOCK = "REPOBEE-SANITIZER-BLOCK"
REPLACE_WITH = "REPOBEE-SANITIZER-REPLACE-WITH"
END_BLOCK = "REPOBEE-SANITIZER-END"

SANITIZER_MARKERS = (
    START_BLOCK,
    REPLACE_WITH,
    END_BLOCK,
)


def check_syntax(lines: List[str]) -> None:
    last = END_BLOCK
    errors = []
    prefix = ""
    has_blocks = False
    for line_number, line in enumerate(lines, start=1):
        if START_BLOCK in line:
            has_blocks = True
            if last != END_BLOCK:
                errors.append(
                    f"Line {line_number}: "
                    "START block must begin file or follow an END block"
                )
            prefix = re.match(rf"(.*?){START_BLOCK}", line).group(1)
            last = START_BLOCK
        elif REPLACE_WITH in line:
            if last != START_BLOCK:
                errors.append(
                    f"Line {line_number}: "
                    "REPLACE-WITH block must follow START block"
                )
            last = REPLACE_WITH
        elif END_BLOCK in line:
            if last not in [START_BLOCK, REPLACE_WITH]:
                errors.append(
                    f"Line {line_number}: "
                    "END block must follow START or REPLACE block"
                )
            last = END_BLOCK

        if (last == REPLACE_WITH or END_BLOCK in line) and not line.startswith(
            prefix
        ):
            errors.append(f"Line {line_number}: Missing prefix")

    if last != END_BLOCK:
        errors.append("Final block must be an END block")

    if not has_blocks:
        errors.append("There are no markers in the file")

    if errors:
        raise plug.PlugError(errors)
