# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.smi import smi, edit

grok.view(smi.PreviewTab)


class PublishForm(edit.SMIPublishForm):
    pass
