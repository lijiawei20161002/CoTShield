"""
Unit tests for LLM-based Intent Reconstructor
Tests shadow intent reconstruction and risk assessment
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from monitor.reconstructor import (
    ShadowIntentReconstructor,
    IntentType,
    ReconstructedIntent
)


class TestReconstructedIntent(unittest.TestCase):
    """Test ReconstructedIntent dataclass"""

    def test_reconstructed_intent_creation(self):
        """Test creation of ReconstructedIntent object"""
        intent = ReconstructedIntent(
            intent_type=IntentType.DECEPTIVE,
            confidence=0.85,
            explanation="Test explanation",
            hidden_reasoning="Hidden thoughts",
            evidence=["Evidence 1", "Evidence 2"],
            risk_assessment="High risk"
        )

        self.assertEqual(intent.intent_type, IntentType.DECEPTIVE)
        self.assertEqual(intent.confidence, 0.85)
        self.assertEqual(intent.explanation, "Test explanation")
        self.assertEqual(len(intent.evidence), 2)


class TestIntentType(unittest.TestCase):
    """Test IntentType enum"""

    def test_all_intent_types_exist(self):
        """Test that all expected intent types are defined"""
        expected_types = [
            'DECEPTIVE',
            'REWARD_HACKING',
            'HIDDEN_REASONING',
            'STRATEGIC_OMISSION',
            'BENIGN'
        ]

        for type_name in expected_types:
            self.assertTrue(hasattr(IntentType, type_name))


class TestShadowIntentReconstructor(unittest.TestCase):
    """Test ShadowIntentReconstructor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.task = "What is 2+2?"
        self.reasoning = "Let me think... 2 plus 2 equals 4."
        self.output = "The answer is 4."

    @patch('monitor.reconstructor.OpenAI')
    def test_openai_reconstructor_initialization(self, mock_openai):
        """Test initialization with OpenAI provider"""
        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key',
            model='gpt-4'
        )

        self.assertEqual(reconstructor.provider, 'openai')
        self.assertEqual(reconstructor.model, 'gpt-4')
        mock_openai.assert_called_once_with(api_key='test-key')

    @patch('monitor.reconstructor.Anthropic')
    def test_anthropic_reconstructor_initialization(self, mock_anthropic):
        """Test initialization with Anthropic provider"""
        reconstructor = ShadowIntentReconstructor(
            provider='anthropic',
            api_key='test-key',
            model='claude-3-opus-20240229'
        )

        self.assertEqual(reconstructor.provider, 'anthropic')
        self.assertEqual(reconstructor.model, 'claude-3-opus-20240229')
        mock_anthropic.assert_called_once_with(api_key='test-key')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'})
    @patch('monitor.reconstructor.OpenAI')
    def test_api_key_from_environment(self, mock_openai):
        """Test API key loaded from environment variable"""
        reconstructor = ShadowIntentReconstructor(provider='openai')
        mock_openai.assert_called_once_with(api_key='env-key')

    @patch('monitor.reconstructor.OpenAI')
    def test_openai_reconstruct_benign(self, mock_openai):
        """Test reconstruction of benign intent with OpenAI"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "BENIGN",
            "confidence": 0.95,
            "explanation": "Straightforward reasoning",
            "hidden_reasoning": "None detected",
            "evidence": ["Clear logic", "Direct answer"],
            "risk_assessment": "Low risk"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task=self.task,
            reasoning=self.reasoning,
            output=self.output
        )

        self.assertIsInstance(result, ReconstructedIntent)
        self.assertEqual(result.intent_type, IntentType.BENIGN)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertIsInstance(result.evidence, list)

    @patch('monitor.reconstructor.Anthropic')
    def test_anthropic_reconstruct_deceptive(self, mock_anthropic):
        """Test reconstruction of deceptive intent with Anthropic"""
        # Mock Anthropic client
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = '''{
            "intent_type": "DECEPTIVE",
            "confidence": 0.82,
            "explanation": "Misleading reasoning detected",
            "hidden_reasoning": "Model appears to be hiding true logic",
            "evidence": ["Inconsistent claims", "Contradictory statements"],
            "risk_assessment": "High risk"
        }'''
        mock_client.messages.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='anthropic',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task="Test task",
            reasoning="Deceptive reasoning here",
            output="Misleading output"
        )

        self.assertIsInstance(result, ReconstructedIntent)
        self.assertEqual(result.intent_type, IntentType.DECEPTIVE)
        self.assertGreater(result.confidence, 0.5)

    @patch('monitor.reconstructor.OpenAI')
    def test_reconstruct_with_context(self, mock_openai):
        """Test reconstruction with additional context"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "BENIGN",
            "confidence": 0.9,
            "explanation": "Test",
            "hidden_reasoning": "None",
            "evidence": [],
            "risk_assessment": "Low"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        context = "User prefers detailed explanations"
        result = reconstructor.reconstruct(
            task=self.task,
            reasoning=self.reasoning,
            output=self.output,
            context=context
        )

        # Verify context was included in the API call
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        self.assertIn(context, user_message)

    @patch('monitor.reconstructor.OpenAI')
    def test_batch_reconstruct(self, mock_openai):
        """Test batch reconstruction of multiple traces"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "BENIGN",
            "confidence": 0.9,
            "explanation": "Test",
            "hidden_reasoning": "None",
            "evidence": [],
            "risk_assessment": "Low"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        traces = [
            {
                'task': 'Task 1',
                'reasoning': 'Reasoning 1',
                'output': 'Output 1'
            },
            {
                'task': 'Task 2',
                'reasoning': 'Reasoning 2',
                'output': 'Output 2'
            }
        ]

        results = reconstructor.batch_reconstruct(traces)

        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], ReconstructedIntent)
        self.assertIsInstance(results[1], ReconstructedIntent)

    @patch('monitor.reconstructor.OpenAI')
    def test_error_handling_invalid_json(self, mock_openai):
        """Test error handling for invalid JSON response"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Invalid JSON {{'
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task=self.task,
            reasoning=self.reasoning,
            output=self.output
        )

        # Should fallback to BENIGN on parse error
        self.assertEqual(result.intent_type, IntentType.BENIGN)
        self.assertIn("parsing error", result.explanation.lower())

    @patch('monitor.reconstructor.OpenAI')
    def test_error_handling_api_failure(self, mock_openai):
        """Test error handling for API call failure"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.chat.completions.create.side_effect = Exception("API Error")

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task=self.task,
            reasoning=self.reasoning,
            output=self.output
        )

        # Should return error intent
        self.assertEqual(result.intent_type, IntentType.BENIGN)
        self.assertIn("error", result.explanation.lower())


class TestIntentTypeDetection(unittest.TestCase):
    """Test detection of different intent types"""

    @patch('monitor.reconstructor.OpenAI')
    def test_reward_hacking_detection(self, mock_openai):
        """Test detection of reward hacking intent"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "REWARD_HACKING",
            "confidence": 0.78,
            "explanation": "Model optimizing for evaluation metrics",
            "hidden_reasoning": "Focusing on what evaluator wants",
            "evidence": ["Metric gaming", "Shortcut taking"],
            "risk_assessment": "Medium-high risk"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task="Optimize this solution",
            reasoning="Let me find the quickest way to score high",
            output="Here's the optimal answer"
        )

        self.assertEqual(result.intent_type, IntentType.REWARD_HACKING)

    @patch('monitor.reconstructor.OpenAI')
    def test_hidden_reasoning_detection(self, mock_openai):
        """Test detection of hidden reasoning"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "HIDDEN_REASONING",
            "confidence": 0.71,
            "explanation": "Important logic not shown",
            "hidden_reasoning": "Key steps omitted from trace",
            "evidence": ["Logic gaps", "Missing steps"],
            "risk_assessment": "Medium risk"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task="Solve this problem",
            reasoning="Let me work on this... done.",
            output="The answer is X"
        )

        self.assertEqual(result.intent_type, IntentType.HIDDEN_REASONING)

    @patch('monitor.reconstructor.OpenAI')
    def test_strategic_omission_detection(self, mock_openai):
        """Test detection of strategic omissions"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "STRATEGIC_OMISSION",
            "confidence": 0.88,
            "explanation": "Deliberately omitting concerns",
            "hidden_reasoning": "Known issues not mentioned",
            "evidence": ["Missing caveats", "Unreported risks"],
            "risk_assessment": "High risk"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task="Recommend approach",
            reasoning="This has risks but...",
            output="This is the best approach"
        )

        self.assertEqual(result.intent_type, IntentType.STRATEGIC_OMISSION)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    @patch('monitor.reconstructor.OpenAI')
    def test_empty_inputs(self, mock_openai):
        """Test handling of empty inputs"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "BENIGN",
            "confidence": 0.5,
            "explanation": "Insufficient data",
            "hidden_reasoning": "None",
            "evidence": [],
            "risk_assessment": "Low"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        result = reconstructor.reconstruct(
            task="",
            reasoning="",
            output=""
        )

        self.assertIsInstance(result, ReconstructedIntent)

    @patch('monitor.reconstructor.OpenAI')
    def test_very_long_inputs(self, mock_openai):
        """Test handling of very long inputs"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "intent_type": "BENIGN",
            "confidence": 0.9,
            "explanation": "Test",
            "hidden_reasoning": "None",
            "evidence": [],
            "risk_assessment": "Low"
        }'''
        mock_client.chat.completions.create.return_value = mock_response

        reconstructor = ShadowIntentReconstructor(
            provider='openai',
            api_key='test-key'
        )

        long_text = "This is a test. " * 1000

        result = reconstructor.reconstruct(
            task=long_text,
            reasoning=long_text,
            output=long_text
        )

        self.assertIsInstance(result, ReconstructedIntent)


if __name__ == '__main__':
    unittest.main()
