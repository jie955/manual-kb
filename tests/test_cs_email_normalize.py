"""Tests for CS email reply post-normalize."""

from generate_answer import audit_cs_email_reply, normalize_cs_email_reply

SAMPLE = """Dear Customer,

Thank you for contacting TOPENS. This is Joyce from TOPENS Customer Service Team. It will be a pleasure to assist you today.

I apologize for any inconvenience this may have caused, but do not worry, we will do our best to help you.

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

Please measure the voltage of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22VDC. If so, please proceed to test
If the voltage is below 22VDC, please check whether the output voltage of the adapter is 36VDC. If so, disconnect the batteries from the control board and measure the output voltage of the batteries to see whether it is above 22VDC. If the voltage of the batteries is also below 22VDC, please keep the batteries charged fully to try it again.
Disconnect all accessories from the control board first (just leave the power source and the arm). And disable the photocell function by turning the dip switch #3 off. Then erase all remotes codes from the control board and reprogram them to have a try. If it fails, please instantaneously short (plug the wire in, then pull it out immediately) the push button terminals (4# and 5#) to check whether the opener can work. You can refer to this video for how to instantaneously short the terminals: https://drive.google.com/file/d/1VdDhyHZxmpQE5pG7BYHOJi5GYb7iZHFS/view?usp=sharing
If there is still no luck, please release the clutches on the arm and push the gate to the middle position firstly. And engage the clutches and press the remote to see whether the gate can run towards the both directions.
Please check the motor. Connect the red & black wires of the arm to the DC 24V power source directly, the motor should run, and then exchange the polarity of the wires, the motor should run in the opposite direction. If the motor runs in both directions, the motor itself is good. Please connect the black & red wires back to the control board and check the next step.
Disconnect the BLUE, GREEN & YELLOW wires of the faulty arm from the control board, use two jumper wires to short the ULT, COM & DLT terminals to which the wires were connected, and then press the remote to see whether the opener can work. Please let me know the result one by one. Videos showing the problem and pictures of the whole control board are much appreciated for further judgement. You can directly send the video to my E-mail via the attachment. If the sending is not successful, please share the photo or video link through dropbox, icloud or google drive. Thanks for your understanding and cooperation. And also please reply your specific SHIPPING ADDRESS with zip code and confirm PHONE # available for further assistance. All TOPENS products are backed by a 12-month warranty. Thank you again for being a valued customer! Your complete satisfaction is what we strive for. We at TOPENS are always standing by and ready to help.
Best regards, Joyce TOPENS Customer Service Team"""


def test_normalize_numbers_five_steps():
    out = normalize_cs_email_reply(SAMPLE)
    assert "1. Please measure" in out
    assert "2. Disconnect all accessories" in out
    assert "3. If there is still no luck" in out
    assert "4. Please check the motor" in out
    assert "5. Disconnect the BLUE" in out
    assert "If the voltage is below 22VDC" in out
    assert "proceed to test" not in out.lower()
    assert "check the next step" not in out.lower()


def test_normalize_footer_outside_last_step():
    out = normalize_cs_email_reply(SAMPLE)
    assert "Please let me know the result one by one" in out
    assert "All TOPENS products are backed by a 12-month warranty" in out
    step5, _, _ = out.partition("5. Disconnect the BLUE")
    m5 = out.split("5. Disconnect the BLUE", 1)[1]
    assert "Please let me know" not in m5.split("\n\nPlease let me know")[0] or (
        "Please let me know" in out and out.index("Please let me know") > out.index("5. Disconnect")
    )


def test_normalize_preserves_signoff():
    out = normalize_cs_email_reply(SAMPLE)
    assert out.strip().endswith("Best regards, Joyce TOPENS Customer Service Team")


def test_normalize_already_numbered_clears_proceed_ref():
    raw = """Dear Customer,

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please measure the voltage of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22VDC. If so, please proceed to test 2. If the voltage is below 22VDC, please check the adapter.
2. Disconnect all accessories from the control board first (just leave the power source and the arm).
3. If there is still no luck, please release the clutches on the arm and push the gate to the middle position firstly.

Please let me know the result one by one.

Best regards,
Joyce
TOPENS Customer Service Team"""
    out = normalize_cs_email_reply(raw)
    assert "proceed to test" not in out.lower()
    assert "check step" not in out.lower()
    assert "1. Please measure" in out
    assert "2. Disconnect all accessories" in out


def test_normalize_already_numbered_inserts_blank_lines():
    raw = """Dear Customer,

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Check all the wires to make sure they are connected securely.
2. If the voltage is normal (above 22V), check whether the power LED on the control board is ON.
3. If the voltage is below 22V, please check whether the output voltage of the adapter is 36VDC.

Please let me know the results of these steps one by one.

Best regards,
Joyce
TOPENS Customer Service Team"""
    out = normalize_cs_email_reply(raw)
    assert "\n\n2. If the voltage is normal" in out
    assert "\n\n3. If the voltage is below" in out
    audit = audit_cs_email_reply(out)
    assert audit["glued_steps"] is False


def test_normalize_numbered_footer_outside_last_step():
    raw = """Dear Customer,

Checked with our engineer, please help us do some tests to find out the problem, so that we can provide corresponding help.

1. Please measure the voltage at the +BAT- terminals (11# and 12#).
2. Disconnect all accessories from the control board first. Please let me know the result one by one. Videos showing the problem are much appreciated.

Best regards,
Joyce
TOPENS Customer Service Team"""
    out = normalize_cs_email_reply(raw)
    assert "2. Disconnect all accessories" in out
    step2_lines = [ln for ln in out.split("\n") if ln.strip().startswith("2.")]
    assert len(step2_lines) == 1
    assert "Please let me know" not in step2_lines[0]
    assert "Please let me know the result one by one" in out
