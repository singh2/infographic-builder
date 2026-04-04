from helpers import read_agent


def _get_step_5_block(content):
    start = content.index("5. **Generate the image")
    end = content.index("\n6. **", start)
    return content[start:end]


def test_step_5b_generates_3_candidates():
    block = _get_step_5_block(read_agent())
    assert "3 candidates" in block.lower() or "three candidates" in block.lower()


def test_step_5b_has_sub_steps():
    block = _get_step_5_block(read_agent())
    assert "5b-i" in block
    assert "5b-ii" in block
    assert "5b-iii" in block


def test_step_5b_i_generates_in_parallel():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "parallel" in lower


def test_step_5b_ii_runs_dealbreaker_check():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "dealbreaker" in lower


def test_step_5b_iii_presents_and_halts():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "present" in lower
    assert "wait" in lower or "halt" in lower or "stop" in lower


def test_step_5b_iii_includes_rationale():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "rationale" in lower


def test_step_5b_references_variation_cascade():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "variation cascade" in lower or "tier" in lower


def test_reconciliation_runs_on_chosen_candidate():
    block = _get_step_5_block(read_agent())
    lower = block.lower()
    assert "chosen" in lower or "selected" in lower or "winner" in lower


def test_single_panel_also_generates_3_candidates():
    block = _get_step_5_block(read_agent())
    single_start = block.lower().find("single-panel")
    assert single_start != -1
    single_section = block[single_start:single_start + 500].lower()
    assert "3 candidates" in single_section or "three candidates" in single_section


def test_single_panel_user_pick_is_final():
    block = _get_step_5_block(read_agent())
    single_start = block.lower().find("single-panel")
    assert single_start != -1
    single_section = block[single_start:single_start + 500].lower()
    assert "final" in single_section or "done" in single_section
