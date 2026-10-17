import os
from atsume.settings import env
import pytest


class TestEnvSettings:
    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ["TEST_ATSUME_INT"] = "123"
        os.environ["TEST_ATSUME_STR"] = "hello"
        os.environ["TEST_ATSUME_BOOL_0"] = "True"
        os.environ["TEST_ATSUME_BOOL_1"] = "true"
        os.environ["TEST_ATSUME_BOOL_2"] = "False"
        os.environ["TEST_ATSUME_BOOL_3"] = "false"

    def test_str(self):
        assert env("TEST_ATSUME_STR") == "hello"