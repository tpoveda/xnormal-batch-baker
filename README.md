# xNormalBatchBakerForMaya

![](http://cgart3d.com/wp-content/uploads/2017/09/xNormalBatchBakerUI.png)
![](http://cgart3d.com/wp-content/uploads/2017/09/xNormalBatchBaker.jpg)

Features
=========================================================
* Nomenclature based workflow
* Similar xNormal UI workflow
* Automatic Photoshop integration
* Normal, AO and Vertex Color baking

Tested on Maya 2016 and Maya 2017

Link to see the tool in action: https://vimeo.com/233740754

Installation
=========================================================
Copy xNormal.pyc, xNormalBatchBakerForMaya.py and xNormalBatchBakerStyle.css files into your Documents/Maya/(Version)/scripts folder. Also, copy logoxNormal.png file to Documents/Maya/(Version)/prefs/icons folder.Execute this code in Maya command panel
``` python
import xNormalBatchBakerForMaya
reload(xNormalBatchBakerForMaya)
```

Dependencies
=========================================================
xNormal.pyc library is a Python wrapper for xNormal: https://github.com/orangeduck/Python-xNormal

To use Photoshop automation features you need to install comtypes Python library: https://pypi.python.org/pypi/comtypes
After install it, copy comtypes folder to Documents/Maya/(Version)/scripts folder
