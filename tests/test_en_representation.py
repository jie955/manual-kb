from en_representation import (
    build_embedding_text_en,
    classify_en_readiness,
    en_retrieval_ready,
)


def test_build_embedding_text_en():
    text = build_embedding_text_en(
        "No Response · DIP #3",
        "1 Disconnect accessories.",
        symptom_keywords="gate does nothing",
    )
    assert "No Response" in text
    assert "Disconnect" in text
    assert "gate does nothing" in text


def test_en_retrieval_ready():
    assert en_retrieval_ready("x" * 80)
    assert not en_retrieval_ready("short")


def test_classify_blocking_tc148():
    assert (
        classify_en_readiness(
            answer_en="",
            answer_zh="x" * 100,
            has_templates=True,
            is_gate_group=True,
        )
        == "blocking"
    )
