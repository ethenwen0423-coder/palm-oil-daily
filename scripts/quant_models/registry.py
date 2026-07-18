"""Central model registry.

To add a model, create another adapter module with ``metadata`` and
``build_contracts`` exports, then append it to ``MODEL_ADAPTERS``.
"""

from . import bollinger_rsi_ma6


MODEL_ADAPTERS = (
    bollinger_rsi_ma6,
)
