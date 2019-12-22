#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains general tests for xNormalBatchBaker
"""

import pytest

from xNormalBatchBaker import __version__


def test_version():
    assert __version__.__version__
