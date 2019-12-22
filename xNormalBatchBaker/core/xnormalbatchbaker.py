#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
xNormal Batch Baker Tool
"""

from __future__ import print_function, division, absolute_import

import tpQtLib


class xNormalBatchBaker(tpQtLib.Window, object):
    def __init__(self):
        super(xNormalBatchBaker, self).__init__(
            name='xNormalBatchBakerWindow',
            title='xNormal Batch Baker',
            size=(350, 700),
            fixed_size=False,
            auto_run=True,
            frame_less=True,
            use_style=False
        )

    def ui(self):
        super(xNormalBatchBaker, self).ui()


def run():
    win = xNormalBatchBaker()
    win.show()
    return win
