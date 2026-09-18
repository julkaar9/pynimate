import re
from unittest.mock import patch

import pytest

from pynimate.choropleth import Choropleth


def test_choropleth_requires_geopandas(sample_geodfr):
    with patch("pynimate._internals.import_module", side_effect=ImportError):
        with pytest.raises(
            ImportError,
            match=re.escape(
                "geopandas is required for Choropleth. Install it with `pip install pynimate[geo]`."
            ),
        ):
            Choropleth(sample_geodfr)
