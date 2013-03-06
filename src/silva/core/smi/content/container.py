# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility, getMultiAdapter
from zope.intid.interfaces import IIntIds

from infrae.comethods import cofunction

from silva.core.messages.interfaces import IMessageService
from silva.core.interfaces import IContainer, IContainerManager, IOrderManager
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces.errors import VersioningError
from silva.ui.interfaces import IJSView
from silva.ui.rest.base import Screen, PageREST, UIREST
from silva.ui.rest.helper import get_notifications
from silva.ui.rest.container import FolderActionREST
from silva.ui.menu import ExpendableMenuItem, ContentMenu
from silva.translations import translate as _


class Container(PageREST):
    grok.adapts(Screen, IContainer)
    grok.name('content')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        view = getMultiAdapter(
            (self.context, self.request), IJSView, name='container')
        return view(self)


class ContainerMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContainer)
    grok.order(10)
    grok.require('silva.ReadSilvaContent')
    name = _('Content')
    screen = Container


class DeleteActionREST(FolderActionREST):
    grok.name('silva.ui.listing.delete')
    grok.require('silva.ChangeSilvaContent')

    def payload(self):
        with IContainerManager(self.context).deleter() as deleter:
            with self.notifier(
                deleter,
                u"Deleted ${contents}.",
                u"Could not delete ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents())
        return {}


class PasteActionREST(FolderActionREST):
    grok.name('silva.ui.listing.paste')
    grok.require('silva.ChangeSilvaContent')

    def payload(self):
        manager = IContainerManager(self.context)

        with manager.copier() as copier:
            with self.notifier(
                copier,
                u"Pasted as a copy ${contents}.",
                u"Could not copy ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents('copied'))

        with manager.mover() as mover:
            with self.notifier(
                mover,
                u"Moved ${contents}.",
                u"Could not move ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents('cutted'))

        return {}


class PasteAsGhostActionREST(FolderActionREST):
    grok.name('silva.ui.listing.pasteasghost')
    grok.require('silva.ChangeSilvaContent')

    def payload(self):
        with IContainerManager(self.context).ghoster() as ghoster:
            with self.notifier(
                ghoster,
                u"Created ghost for ${contents}.",
                u"Could not create ghost for ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents('copied'))
        return {}


class RenameActionREST(FolderActionREST):
    grok.name('silva.ui.listing.rename')
    grok.require('silva.ChangeSilvaContent')

    def get_renaming_information(self):
        form = self.request.form
        total = int(form.get('values', 0))

        for index in range(total):
            for content in self.get_contents(form.get('values.%d.id' % index)):
                # This will loop at best one time, none if there is a problem
                identifier = form.get('values.%d.identifier' % index)
                title = form.get('values.%d.title' % index)
                if identifier is not None or title is not None:
                    yield (content, identifier, title)

    def payload(self):
        with IContainerManager(self.context).renamer() as renamer:
            with self.notifier(
                renamer,
                u"Renamed ${contents}.",
                u"Could not rename ${contents}: ${reason}") as notifier:
                notifier.map(self.get_renaming_information())
        return {}


class PublicationFolderActionREST(FolderActionREST):
    grok.baseclass()

    def workflow_action(self, workflow):
        raise NotImplementedError

    @cofunction
    def workflow_processor(self):
        content = yield
        while content is not None:
            workflow = IPublicationWorkflow(content, None)
            if workflow is not None:
                try:
                    self.workflow_action(workflow)
                except VersioningError as error:
                    result = error
                else:
                    result = content
            else:
                result = VersioningError(
                    _(u"This action is not applicable on this item."),
                    content)
            content = yield result


class PublishActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.publish')

    def workflow_action(self, workflow):
        workflow.publish()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"Published ${contents}.",
                u"Could not publish ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents(recursive=True))
        return {}


class CloseActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.close')

    def workflow_action(self, workflow):
        workflow.close()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"Closed ${contents}.",
                u"Could not close ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents(recursive=True))
        return {}


class NewVersionActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.newversion')

    def workflow_action(self, workflow):
        workflow.new_version()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"New version(s) created for ${contents}.",
                u"Could not create new version(s) for "
                u"${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents())
        return {}


class RejectRequestActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.rejectrequest')

    def workflow_action(self, workflow):
        workflow.reject_request()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"Publication rejected for ${contents}.",
                u"Could not reject publication for "
                u" ${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents())
        return {}


class WithdrawRequestActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.withdrawrequest')

    def workflow_action(self, workflow):
        workflow.withdraw_request()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"Publication request withdrawn for ${contents}.",
                u"Could not withdraw publication request for "
                u"${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents())
        return {}


class RequestApprovalActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.requestapproval')

    def workflow_action(self, workflow):
        workflow.request_approval()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"Approval for publication requested for ${contents}.",
                u"Could not request publication approval for "
                u"${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents())
        return {}


class RevokeApprovalActionREST(PublicationFolderActionREST):
    grok.name('silva.ui.listing.revokeapproval')

    def workflow_action(self, workflow):
        workflow.revoke_approval()

    def payload(self):
        with self.workflow_processor() as processor:
            with self.notifier(
                processor,
                u"Approval canceled for ${contents}.",
                u"Could not cancel approval for "
                u"${contents}: ${reason}") as notifier:
                notifier.map(self.get_selected_contents())
        return {}


class OrderREST(UIREST):
    grok.context(IContainer)
    grok.name('silva.ui.listing.order')
    grok.require('silva.ChangeSilvaContent')

    def get_integer(self, name):
        try:
            return int(self.request.form.get(name, '-1'))
        except ValueError:
            return -1

    def notify(self, message, type=u""):
        service = getUtility(IMessageService)
        service.send(message, self.request, namespace=type)

    def POST(self):
        position = self.get_integer('position')
        content = self.get_integer('content')

        if (position >= 0 and content >= 0 and
            IOrderManager(self.context).move(
                getUtility(IIntIds).getObject(content),
                position)):
            success = True
            self.notify(
                _(u'Item moved in position ${position}.',
                  mapping={'position': position + 1}),
                type='feedback')
        else:
            success = False
            self.notify(
                _(u'Could not move item in position ${position}.',
                  mapping={'position': position + 1}),
                type='error')

        data = {'content': success}
        get_notifications(self, data)

        return self.json_response(data)

