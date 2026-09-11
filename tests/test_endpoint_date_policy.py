import unittest

from scripts.endpoint_date_policy import expected_response_date


class EndpointDatePolicyTests(unittest.TestCase):
    T0 = "2026-09-10"
    D = "2026-09-11"

    def test_historical_endpoints_use_t0(self):
        self.assertEqual(
            expected_response_date("futures-options-chain", t0=self.T0, analysis_date=self.D),
            self.T0,
        )
        self.assertEqual(
            expected_response_date("options-gamma-levels", t0=self.T0, analysis_date=self.D),
            self.T0,
        )

    def test_night_endpoints_use_analysis_date(self):
        self.assertEqual(
            expected_response_date("futures-price-after-hours", t0=self.T0, analysis_date=self.D),
            self.D,
        )
        self.assertEqual(
            expected_response_date("options-institutional-after-hours", t0=self.T0, analysis_date=self.D),
            self.D,
        )
        self.assertEqual(
            expected_response_date("options-after-hours", t0=self.T0, analysis_date=self.D),
            self.D,
        )

    def test_dataless_regular_endpoints_have_no_global_date_check(self):
        self.assertIsNone(
            expected_response_date("options-institutional", t0=self.T0, analysis_date=self.D)
        )
        self.assertIsNone(
            expected_response_date("futures-institutional", t0=self.T0, analysis_date=self.D)
        )


if __name__ == "__main__":
    unittest.main()
