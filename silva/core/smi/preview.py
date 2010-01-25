# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi import smi, edit

from five import grok


grok.view(smi.PreviewTab)


class PublishNowButton(edit.PublishNowButton):
    pass
