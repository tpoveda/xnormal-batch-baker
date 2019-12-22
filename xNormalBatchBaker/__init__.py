#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for xNormalBatchBaker
"""

from __future__ import print_function, division, absolute_import

import os
import inspect

from tpPyUtils import importer
from tpQtLib.core import resource as resource_utils

# =================================================================================

logger = None
resource = None

# =================================================================================


class xNormalBatchBakerResource(resource_utils.Resource, object):
    RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class xNormalBatchBaker(importer.Importer, object):
    def __init__(self, *args, **kwargs):
        super(xNormalBatchBaker, self).__init__(module_name='xNormalBatchBaker', *args, **kwargs)

    def get_module_path(self):
        """
        Returns path where xNormalBatchBaker module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import xNormalBatchBaker
                    mod_dir = xNormalBatchBaker.__path__[0]
                except Exception:
                    return None

        return mod_dir


def init(do_reload=False, dev=False):
    """
    Initializes module
    :param do_reload: bool, Whether to reload modules or not
    """

    if not dev:
        import tpPyUtils
        tpPyUtils.init(do_reload=do_reload)
        import tpDccLib
        tpDccLib.init(do_reload=do_reload)
        import tpQtLib
        tpQtLib.init(do_reload=do_reload)

    xnormal_importer = importer.init_importer(importer_class=xNormalBatchBaker, do_reload=do_reload, debug=dev)

    global logger
    global resource
    logger = xnormal_importer.logger
    resource = xNormalBatchBakerResource

    xnormal_importer.import_modules()
    xnormal_importer.import_packages(only_packages=True)
    if do_reload:
        xnormal_importer.reload_all()


def run(do_reload=False):
    init(do_reload=do_reload)
    from xNormalBatchBaker.core import xnormalbatchbaker
    win = xnormalbatchbaker.run()
    return win
