import pytest
import os
from .main import Objects

Objects.objPath = os.environ.get('pathObj')
