#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from negotiation_utils import (
    extract_negotiation_clauses,
    negotiation_offers_from_text,
    strip_negotiation_from_text,
)

QA_023_TAIL = (
    "If the problem disappear in the above step, adding some load to the gate motor "
    "by connecting a resistor to the BLACK & RED wires of the arm in parallel to solve "
    "the problem. Regretfully, we do not have this resistor for sale in our store. "
    "Sorry for the inconvenience. Instead, you can purchase the resistors via the "
    "following link. If you are willing to try the resistor, we would like to send "
    "you two M12 remotes to cover the cost of the resistor. Is it acceptable?"
)


class TestNegotiationUtils(unittest.TestCase):
    def test_qa_023_extracts_offer(self):
        clauses = extract_negotiation_clauses(QA_023_TAIL)
        self.assertTrue(any("M12 remotes" in c for c in clauses))
        self.assertTrue(any("acceptable" in c.lower() for c in clauses))

    def test_qa_023_strips_but_keeps_purchase_intro(self):
        cleaned, offers = strip_negotiation_from_text(QA_023_TAIL)
        self.assertTrue(any("M12" in o for o in offers))
        self.assertIn("purchase the resistors", cleaned)
        self.assertNotIn("M12 remotes", cleaned)
        self.assertNotIn("acceptable", cleaned.lower())

    def test_no_disclaimer_no_strip_on_generic_text(self):
        text = "Please replace the remote battery and try again."
        cleaned, offers = strip_negotiation_from_text(text)
        self.assertEqual(cleaned, text)
        self.assertEqual(offers, [])


if __name__ == "__main__":
    unittest.main()
