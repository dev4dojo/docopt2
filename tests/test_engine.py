from docopt2.engine import MatchContext, Matcher
from docopt2.nodes import ArgumentNode, ChoiceGroup, CommandNode, OptionalGroup, OptionNode, RequiredGroup


def test_engine_match_argument() -> None:
    """Verifies that an ArgumentNode consumes a positional value."""
    node = ArgumentNode("<file>")
    ctx = MatchContext(left=("image.png",))

    result = Matcher(ctx).match(node)

    assert result is not None
    assert result.to_dict() == {"<file>": "image.png"}
    assert result.left == ()  # Arg was consumed


def test_engine_match_command() -> None:
    """Verifies that a CommandNode matches only the specific keyword."""
    node = CommandNode("move")

    # Success case
    ctx_ok = MatchContext(left=("move", "other"))
    result_ok = Matcher(ctx_ok).match(node)
    assert result_ok is not None
    assert result_ok.to_dict() == {"move": True}
    assert result_ok.left == ("other",)

    # Failure case
    ctx_fail = MatchContext(left=("copy",))
    assert Matcher(ctx_fail).match(node) is None


def test_engine_match_option() -> None:
    """Verifies short and long flag matching."""
    node = OptionNode(name="--verbose", short="-v", long="--verbose")

    # Match short
    res_short = Matcher(MatchContext(left=("-v",))).match(node)
    assert res_short is not None and res_short.to_dict()["--verbose"] is True

    # Match long
    res_long = Matcher(MatchContext(left=("--verbose",))).match(node)
    assert res_long is not None and res_long.to_dict()["--verbose"] is True


def test_engine_required_group() -> None:
    """Verifies that ALL children in a RequiredGroup must match."""
    node = RequiredGroup((CommandNode("move"), ArgumentNode("<file>")))

    # Success
    ctx = MatchContext(left=("move", "a.txt"))
    result = Matcher(ctx).match(node)
    assert result is not None
    assert result.to_dict() == {"move": True, "<file>": "a.txt"}

    # Failure (missing one part)
    assert Matcher(MatchContext(left=("move",))).match(node) is None


def test_engine_choice_group_backtracking() -> None:
    """Verifies that ChoiceGroup tries branches until one succeeds."""
    # ( move | copy )
    node = ChoiceGroup((CommandNode("move"), CommandNode("copy")))

    # Match first branch
    res_move = Matcher(MatchContext(left=("move",))).match(node)
    assert res_move is not None and "move" in res_move.to_dict()

    # Match second branch
    res_copy = Matcher(MatchContext(left=("copy",))).match(node)
    assert res_copy is not None and "copy" in res_copy.to_dict()


def test_engine_optional_group() -> None:
    """Verifies that OptionalGroup never fails the match, only consumes if possible."""
    # [ --force ]
    node = OptionalGroup((OptionNode("--force", long="--force"),))

    # Case: Option is present
    res_present = Matcher(MatchContext(left=("--force", "file"))).match(node)
    assert res_present is not None
    assert res_present.to_dict() == {"--force": True}
    assert res_present.left == ("file",)

    # Case: Option is missing (Should NOT fail, just return original context)
    res_missing = Matcher(MatchContext(left=("file",))).match(node)
    assert res_missing is not None
    assert res_missing.to_dict() == {}
    assert res_missing.left == ("file",)
