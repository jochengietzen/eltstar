import time

from eltstar_engine_pandas.engine import PandasEngine

from eltstar.logging import logger
from eltstar.testing.faker_manager import FakerManager
from eltstar_pandas_example.models.youtube import tech_channels

if __name__ == "__main__":
    faker_manager = FakerManager()
    for i in [10, 100, 1000]:
        start = time.time()
        df = faker_manager.generate(table=tech_channels, engine=PandasEngine(), n_values=i).data_frame
        logger.debug("Generated %d rows in %.4f seconds", i, time.time() - start)

    print(df)
