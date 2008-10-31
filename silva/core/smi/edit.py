# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi import properties
from silva.core.smi import smi
from silva.core import conf as silvaconf

from Products.Silva import interfaces

silvaconf.templatedir('templates')
silvaconf.view(smi.EditTab)

class PublishNowButton(properties.PublishNowButton):

    silvaconf.context(interfaces.IVersionedContent)
