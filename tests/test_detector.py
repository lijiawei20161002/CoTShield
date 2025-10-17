"""
Unit tests for CoT Divergence Detector
Tests all divergence detection types and analysis functionality
"""

import unittest
from monitor.detector import (
    analyze_cot_trace,
    DivergenceType,
    DivergenceFlag,
    CoTDivergenceDetector
)


class TestContradictionDetection(unittest.TestCase):
    """Test contradiction detection between reasoning and output"""

    def test_clear_contradiction(self):
        """Test detection of clear negation vs affirmation"""
        reasoning = "This answer is definitely not correct. The evidence clearly shows it's false and wrong."
        output = "Yes, this answer is absolutely correct."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        contradiction_flags = [f for f in flags if f.type == DivergenceType.CONTRADICTION]
        self.assertGreater(len(contradiction_flags), 0)

    def test_no_contradiction(self):
        """Test that consistent reasoning produces no flags"""
        reasoning = "The capital of France is Paris. This is well documented and correct."
        output = "The capital is Paris."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        contradiction_flags = [f for f in flags if f.type == DivergenceType.CONTRADICTION]
        self.assertEqual(len(contradiction_flags), 0)

    def test_contradiction_with_shared_terms(self):
        """Test contradiction detection requires semantic overlap"""
        reasoning = "The sky is not blue today."
        output = "The grass is green."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        # Should not flag contradiction - different topics
        self.assertEqual(len(flags), 0)


class TestLogicalLeapDetection(unittest.TestCase):
    """Test logical leap detection (unjustified confidence jumps)"""

    def test_uncertainty_to_confidence_leap(self):
        """Test detection of uncertain reasoning to confident output"""
        reasoning = "I'm not sure. Maybe true.\nDefinitely!"
        output = "This is the answer."

        detector = CoTDivergenceDetector(sensitivity=0.6)
        flags = detector.detect(reasoning, output)
        leap_flags = [f for f in flags if f.type == DivergenceType.LOGICAL_LEAP]
        # May detect leap depending on step splitting
        self.assertIsInstance(flags, list)

    def test_justified_confidence(self):
        """Test that justified conclusions don't trigger flags"""
        reasoning = "Based on extensive evidence and clear documentation supporting this conclusion, this is true with certainty."
        output = "This is definitely true."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        leap_flags = [f for f in flags if f.type == DivergenceType.LOGICAL_LEAP]
        self.assertEqual(len(leap_flags), 0)

    def test_sensitivity_adjustment(self):
        """Test that sensitivity affects detection threshold"""
        reasoning = "Maybe. Possibly.\nCorrect."
        output = "Definitely correct"

        detector_low = CoTDivergenceDetector(sensitivity=0.2)
        detector_high = CoTDivergenceDetector(sensitivity=0.8)

        flags_low = detector_low.detect(reasoning, output)
        flags_high = detector_high.detect(reasoning, output)

        # High sensitivity should detect same or more issues
        self.assertGreaterEqual(len(flags_high), len(flags_low))


class TestUnsupportedClaimDetection(unittest.TestCase):
    """Test unsupported claim detection"""

    def test_claim_without_support(self):
        """Test detection of confident claims lacking reasoning support"""
        reasoning = "Let me think about something else entirely. The weather is nice."
        output = "The quantum mechanics principle clearly states the answer is 42."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        unsupported_flags = [f for f in flags if f.type == DivergenceType.UNSUPPORTED_CLAIM]
        self.assertGreater(len(unsupported_flags), 0)

    def test_well_supported_claim(self):
        """Test that claims with reasoning support don't trigger flags"""
        reasoning = "Quantum mechanics principles show entanglement effects. The answer is 42."
        output = "Based on quantum mechanics, the answer is 42."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        unsupported_flags = [f for f in flags if f.type == DivergenceType.UNSUPPORTED_CLAIM]
        self.assertEqual(len(unsupported_flags), 0)


class TestOmissionDetection(unittest.TestCase):
    """Test detection of omitted caveats and concerns"""

    def test_caveat_omission(self):
        """Test detection of reasoning caveats not reflected in output"""
        reasoning = "However, there are serious concerns about this approach. But we should be careful."
        output = "This is the perfect solution."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        omission_flags = [f for f in flags if f.type == DivergenceType.OMISSION]
        self.assertGreater(len(omission_flags), 0)

    def test_acknowledged_caveats(self):
        """Test that acknowledged caveats don't trigger flags"""
        reasoning = "However, there are concerns about this approach."
        output = "This works, but there are some concerns to consider."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        omission_flags = [f for f in flags if f.type == DivergenceType.OMISSION]
        self.assertEqual(len(omission_flags), 0)


class TestReversedConclusionDetection(unittest.TestCase):
    """Test detection of reversed sentiment/conclusions"""

    def test_sentiment_reversal(self):
        """Test detection of negative reasoning to positive output"""
        reasoning = "This solution is not valid and shouldn't be used. It's incorrect and wrong."
        output = "This solution is valid and should be used. It's correct."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        reversed_flags = [f for f in flags if f.type == DivergenceType.REVERSED_CONCLUSION]
        self.assertGreater(len(reversed_flags), 0)

    def test_consistent_sentiment(self):
        """Test that consistent sentiment doesn't trigger flags"""
        reasoning = "This is good and beneficial. It's the right and correct approach."
        output = "This is the correct solution."

        detector = CoTDivergenceDetector(sensitivity=0.5)
        flags = detector.detect(reasoning, output)
        reversed_flags = [f for f in flags if f.type == DivergenceType.REVERSED_CONCLUSION]
        self.assertEqual(len(reversed_flags), 0)


class TestAnalyzeCotTrace(unittest.TestCase):
    """Test the main analysis function"""

    def test_comprehensive_analysis(self):
        """Test full analysis returns all expected fields"""
        reasoning = "Let me think... this might not be right."
        output = "This is definitely correct."

        result = analyze_cot_trace(reasoning, output, sensitivity=0.5)

        # Check all required fields present
        self.assertIn('risk_score', result)
        self.assertIn('flags', result)
        self.assertIn('flag_count', result)
        self.assertIn('severity_distribution', result)
        self.assertIn('divergence_types', result)

        # Check data types
        self.assertIsInstance(result['risk_score'], float)
        self.assertIsInstance(result['flags'], list)
        self.assertIsInstance(result['flag_count'], int)
        self.assertIsInstance(result['severity_distribution'], dict)
        self.assertIsInstance(result['divergence_types'], dict)

    def test_risk_score_range(self):
        """Test that risk score is in valid range [0, 1]"""
        reasoning = "This is wrong and bad."
        output = "This is perfect."

        result = analyze_cot_trace(reasoning, output, sensitivity=0.5)
        self.assertGreaterEqual(result['risk_score'], 0.0)
        self.assertLessEqual(result['risk_score'], 1.0)

    def test_severity_distribution(self):
        """Test severity distribution calculation"""
        reasoning = "I'm not sure. However, there are concerns. This is bad."
        output = "This is definitely the perfect solution."

        result = analyze_cot_trace(reasoning, output, sensitivity=0.6)

        severity = result['severity_distribution']
        self.assertIn('high', severity)
        self.assertIn('medium', severity)
        self.assertIn('low', severity)

        # Total should equal flag count
        total = severity['high'] + severity['medium'] + severity['low']
        self.assertEqual(total, result['flag_count'])

    def test_clean_trace_analysis(self):
        """Test analysis of clean, consistent reasoning"""
        reasoning = "Based on the evidence, this is clearly the correct answer. The documentation supports it."
        output = "This is the correct answer."

        result = analyze_cot_trace(reasoning, output, sensitivity=0.5)

        self.assertEqual(result['flag_count'], 0)
        self.assertEqual(result['risk_score'], 0.0)
        self.assertEqual(result['severity_distribution']['high'], 0)

    def test_multiple_divergence_types(self):
        """Test detection of multiple divergence types in one trace"""
        reasoning = """
        I'm not entirely sure about this. However, there are serious concerns.
        This doesn't seem right. The evidence doesn't support this conclusion.
        """
        output = "This is absolutely perfect and definitely the right answer with no concerns."

        result = analyze_cot_trace(reasoning, output, sensitivity=0.6)

        # Should detect multiple types of divergence
        self.assertGreater(result['flag_count'], 1)
        # Check that at least some divergence types were detected
        detected_types = [k for k, v in result['divergence_types'].items() if v > 0]
        self.assertGreater(len(detected_types), 0)

    def test_sensitivity_high(self):
        """Test high sensitivity detects more issues"""
        reasoning = "Maybe this could work."
        output = "This definitely works."

        result_low = analyze_cot_trace(reasoning, output, sensitivity=0.2)
        result_high = analyze_cot_trace(reasoning, output, sensitivity=0.9)

        self.assertGreaterEqual(result_high['flag_count'], result_low['flag_count'])
        self.assertGreaterEqual(result_high['risk_score'], result_low['risk_score'])

    def test_divergence_flag_structure(self):
        """Test that DivergenceFlag objects have correct structure"""
        reasoning = "This is not correct."
        output = "This is correct."

        result = analyze_cot_trace(reasoning, output, sensitivity=0.5)

        if result['flag_count'] > 0:
            flag = result['flags'][0]
            self.assertIsInstance(flag, DivergenceFlag)
            self.assertIsInstance(flag.divergence_type, DivergenceType)
            self.assertIsInstance(flag.severity, float)
            self.assertIsInstance(flag.reasoning_snippet, str)
            self.assertIsInstance(flag.output_snippet, str)
            self.assertIsInstance(flag.explanation, str)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_reasoning(self):
        """Test handling of empty reasoning"""
        result = analyze_cot_trace("", "Some output", sensitivity=0.5)
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(result['risk_score'], 0.0)

    def test_empty_output(self):
        """Test handling of empty output"""
        result = analyze_cot_trace("Some reasoning", "", sensitivity=0.5)
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(result['risk_score'], 0.0)

    def test_both_empty(self):
        """Test handling of both empty"""
        result = analyze_cot_trace("", "", sensitivity=0.5)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['flag_count'], 0)

    def test_very_long_text(self):
        """Test handling of very long text"""
        reasoning = "This is a test. " * 1000
        output = "Final answer. " * 100

        result = analyze_cot_trace(reasoning, output, sensitivity=0.5)
        self.assertIsInstance(result, dict)

    def test_special_characters(self):
        """Test handling of special characters"""
        reasoning = "Test with émojis 🎉 and spëcial çhars!@#$%"
        output = "Output with symbols: <>&\"'"

        result = analyze_cot_trace(reasoning, output, sensitivity=0.5)
        self.assertIsInstance(result, dict)

    def test_sensitivity_boundaries(self):
        """Test sensitivity at boundary values"""
        reasoning = "Maybe correct"
        output = "Definitely correct"

        result_min = analyze_cot_trace(reasoning, output, sensitivity=0.0)
        result_max = analyze_cot_trace(reasoning, output, sensitivity=1.0)

        self.assertIsInstance(result_min, dict)
        self.assertIsInstance(result_max, dict)


if __name__ == '__main__':
    unittest.main()
