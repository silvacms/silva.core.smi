# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from AccessControl.security import checkPermission

from silva.core.interfaces import IVersionedContent
from silva.core.views import views as silvaviews
from silva.core.smi.content.publish import Publish
from zeam.form import silva as silvaforms


class PublicationInfo(silvaviews.Viewlet):
    """Portlet giving information about the publication status.
    """
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.viewletmanager(silvaforms.SMIFormPortlets)
    grok.order(10)

    def update(self):
        format = self.request.locale.dates.getFormatter('dateTime', 'short').format
        convert = lambda d: d is not None and format(d.asdatetime()) or None
        self.publication_date = convert(
            self.context.get_public_version_publication_datetime())
        self.expiration_date = convert(
            self.context.get_public_version_expiration_datetime())
        self.have_unapproved = self.context.get_unapproved_version() != None
        self.have_next = self.context.get_next_version() != None
        self.have_closed = self.context.get_last_closed_version() != None
        self.have_approved = self.context.is_approved()
        self.have_published = self.context.is_published()
        self.may_approve = checkPermission('silva.ApproveSilvaContent', self.context)
        self.may_change = checkPermission('silva.ChangeSilvaContent', self.context)

