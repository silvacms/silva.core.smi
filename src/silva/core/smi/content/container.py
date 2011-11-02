# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from infrae.comethods import comethod

from silva.core.messages.interfaces import IMessageService
from silva.core.interfaces import IContainer, IContainerManager, IOrderManager
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces.errors import VersioningError, PublicationError
from silva.ui.rest.base import Screen, PageREST, UIREST
from silva.ui.rest.container import ContentSerializer
from silva.ui.rest.container import FolderActionREST
from silva.ui.menu import ExpendableMenuItem, ContentMenu
from silva.translations import translate as _


class Container(PageREST):
    grok.adapts(Screen, IContainer)
    grok.name('content')
    grok.require('silva.ReadSilvaContent')

    def get_publishable_content(self):
        """Return all the publishable content of the container.
        """
        default = self.context.get_default()
        if default is not None:
            yield default
        for content in self.context.get_ordered_publishables():
            yield content

    def get_non_publishable_content(self):
        """Return all the non-publishable content of the container.
        """
        for content in self.context.get_non_publishables():
            yield content

    def payload(self):
        serializer = ContentSerializer(self, self.request)
        return {
            "ifaces": ["listing"],
            "content": serializer(self.context),
            "items": {
                "publishables": map(serializer, self.get_publishable_content()),
                "assets": map(serializer, self.get_non_publishable_content())}}


class ContainerMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContainer)
    grok.order(10)
    grok.require('silva.ReadSilvaContent')
    name = _('Content')
    screen = Container


class DeleteActionREST(FolderActionREST):
    grok.name('silva.ui.listing.delete')

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

    def payload(self):
        manager = IContainerManager(self.context)

        with manager.copier() as copier:
            with self.notifier(
                copier,
                u"Pasted as a copy ${contents}",
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

    @comethod
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
                result = PublicationError(
                    _(u"This action is not applicable on this content."),
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
                u"Could not create new version(s) for ${contents}: ${reason}") as notifier:
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
                _(u'Content moved in position ${position}.',
                  mapping={'position': position + 1}),
                type='feedback')
        else:
            success = False
            self.notify(
                _(u'Could not move content in position ${position}.',
                  mapping={'position': position + 1}),
                type='error')

        return self.json_response({
                'content': success,
                'notifications': self.get_notifications()})

