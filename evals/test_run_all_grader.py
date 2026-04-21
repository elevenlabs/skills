import importlib.util
import unittest
from pathlib import Path


def load_run_all_module():
    module_path = Path(__file__).with_name("run_all.py")
    spec = importlib.util.spec_from_file_location("evals_run_all", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


run_all = load_run_all_module()


class RunAllGraderTests(unittest.TestCase):
    def test_sound_effect_prompt_influence_counts_as_high_adherence(self):
        response = """
        The Python script calls ElevenLabs with:
        - duration_seconds=8.0
        - prompt_influence=0.85
        - loop=True
        """
        passed, evidence = run_all.check_expectation(
            response.lower(),
            response,
            "Sets prompt_influence or equivalent parameter for high adherence",
        )
        self.assertTrue(passed, evidence)

    def test_music_duration_accepts_raw_milliseconds(self):
        response = """
        The Python script calls the ElevenLabs Music API with custom lyrics about coding late at night
        and requests 60000 ms of audio.
        """
        passed, evidence = run_all.check_expectation(
            response.lower(),
            response,
            "Sets duration to approximately 60 seconds (60000ms)",
        )
        self.assertTrue(passed, evidence)

    def test_agent_cli_eval_accepts_successful_project_creation_without_literal_commands(self):
        response = """
        Created an ElevenLabs CLI project under outputs/restaurant-reservation-agent and used it to
        create and push a voice agent.
        """
        passed, evidence = run_all.check_expectation(
            response.lower(),
            response,
            "Uses 'elevenlabs agents init' or equivalent CLI command to set up the project",
        )
        self.assertTrue(passed, evidence)

    def test_api_key_validation_accepts_verified_wording_without_curl(self):
        response = """
        ELEVENLABS_API_KEY is already set in this environment, and I verified it successfully against
        ElevenLabs. No setup is needed right now.
        """
        passed, evidence = run_all.check_expectation(
            response.lower(),
            response,
            "Validates the key by making a test API call to the user endpoint",
        )
        self.assertTrue(passed, evidence)

    def test_sdk_constructor_detected_from_client_assignment(self):
        response = """
        from elevenlabs import ElevenLabs

        client = ElevenLabs()
        """
        passed, evidence = run_all.check_expectation(
            response.lower(),
            response,
            "Creates a client with ElevenLabs()",
        )
        self.assertTrue(passed, evidence)

    def test_output_requirement_accepts_explicit_named_file_without_write_keywords(self):
        response = """
        Created outputs/hello.mp3 and verified the output file exists and is a valid MP3.
        """
        passed, evidence = run_all.check_expectation(
            response.lower(),
            response,
            "Writes output to a file named hello.mp3",
        )
        self.assertTrue(passed, evidence)
