xNormalBatchBaker
============================================================

.. image:: https://img.shields.io/github/license/tpoveda/xNormalBatchBaker.svg
    :target: https://github.com/tpoveda/xNormalBatchBaker/blob/master/LICENSE

Tool that allows 3d artists to smooth its workflow when baking maps using xNormal

Features
-------------------

* Nomenclature based workflow
* Similar xNormal UI workflow
* Automatic Photoshop integration
* Normal, AO and Vertex Color baking

Dependencies
-------------------

* **tpPyUtils**: https://github.com/tpoveda/tpPyUtils
* **tpDccLib**: https://github.com/tpoveda/tpDccLib
* **tpQtLib**: https://github.com/tpoveda/tpQtLib
* **xNormal.py**: https://github.com/orangeduck/Python-xNormal

Depending on the DCC you are going to use you will need to download and install one of the following repositories:

* **3ds Max**: https://github.com/tpoveda/tpMaxLib
* **Maya**: https://github.com/tpoveda/tpMayaLib
* **Blender**: *Work in Progress*

Installation
-------------------

Manual
~~~~~~~~~~~~~~~~~~~~~~

1. Clone/Download **xNormalBatchBaker dependencies** Python packages and follow instructions to install them.
2. Clone/Download **xNormalBatchBaker** anywhere in your PC (If you download the repo, you will need to extract the contents of the .zip file).
3. Copy **xNormalBatchBaker** folder located inside **source** folder in a path added to **sys.path**

Automatic
~~~~~~~~~~~~~~~~~~~~~~
Automatic installation for tpRenamer is not finished yet.

Usage
-------------------

Initialization Code
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import xNormalBatchBaker
    xNormalBatchBaker.run()