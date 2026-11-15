# Pipeline tests

Place tests next to the preprocessing or scoring behavior they verify. Keep each test tied to its input version, units, grid, and expected QA behaviour.

The repository's available pipeline tests are listed by pytest configuration in pyproject.toml. A test result is evidence only for the exercised code and fixture; it does not prove global coverage or accuracy of untested data.
