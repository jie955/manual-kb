from en_representation import (
    append_email_verbatim_to_embedding,
    email_example_sources_csv,
    email_verbatim_from_example,
)


def test_email_verbatim_from_example_keys():
    assert email_verbatim_from_example({"verbatim": "gate stuck"}) == "gate stuck"
    assert email_verbatim_from_example({"customer_verbatim": "motor ok"}) == "motor ok"
    assert email_verbatim_from_example({"verbatim": "a", "customer_verbatim": "b"}) == "a"


def test_append_email_verbatim_to_embedding():
    base = "No Response · DIP #3\n1 Disconnect accessories."
    out = append_email_verbatim_to_embedding(
        base,
        [
            {
                "scenario_id": "cs_0001",
                "verbatim": "the gate does nothing when i push the button",
            }
        ],
    )
    assert "[Customer reported variants]" in out
    assert "[Customer email · cs_0001]" in out
    assert "gate does nothing" in out
    assert out.startswith("No Response")


def test_append_email_verbatim_empty():
    assert append_email_verbatim_to_embedding("base", []) == "base"
    assert append_email_verbatim_to_embedding("base", None) == "base"


def test_email_example_sources_csv():
    csv = email_example_sources_csv(
        [{"scenario_id": "cs_0001"}, {"scenario_id": "cs_0013"}]
    )
    assert csv == "cs_0001,cs_0013"
