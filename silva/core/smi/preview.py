# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.smi import smi, edit


silvaconf.view(smi.PreviewTab)


class PublishNowButton(edit.PublishNowButton):
    pass
