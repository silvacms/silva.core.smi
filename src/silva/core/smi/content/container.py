# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from silva.core.messages.interfaces import IMessageService
from silva.core.interfaces import IContainer, IContainerManager, IOrderManager
from silva.core.interfaces import IPublicationWorkflow, PublicationWorkflowError
from silva.ui.rest.base import Screen, PageREST, UIREST
from silva.ui.rest.container import ContentSerializer, ContentCounter, ActionREST
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
        return {"ifaces": ["listing"],
                "content": serializer(self.context),
                "items": {"publishables": map(serializer, self.get_publishable_content()),
                          "assets": map(serializer, self.get_non_publishable_content())}}




class ContainerMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContainer)
    grok.order(10)
    name = _('Content')
    screen = Container


class DeleteActionREST(ActionREST):
    grok.name('silva.ui.listing.delete')

    def payload(self):
        success = ContentCounter(self)
        failures = ContentCounter(self)
        manager = IContainerManager(self.context)

        with manager.deleter() as deleter:
            for identifier, content in self.get_selected_content():
                if deleter.add(content):
                    success.append(content)
                    self.remove_from_listing(identifier)
                else:
                    failures.append(content)

        # Compute notification message
        if success:
            if failures:
                self.notify(
                    _(u'Deleted ${deleted} but could not delete ${not_deleted}.',
                      mapping={'deleted': success,
                               'not_deleted': failures}))
            else:
                self.notify(
                    _(u'Deleted ${deleted}.',
                      mapping={'deleted': success}))
        elif failures:
            self.notify(
                _(u'Could not delete ${not_deleted}.',
                  mapping={'not_deleted': failures}))
        return {}


class PasteActionREST(ActionREST):
    grok.name('silva.ui.listing.paste')

    def payload(self):
        copied_failures = ContentCounter(self)
        copied_success = ContentCounter(self)
        moved_failures = ContentCounter(self)
        moved_success = ContentCounter(self)

        manager = IContainerManager(self.context)

        with manager.copier() as copier:
            for identifier, content in self.get_selected_content('copied'):
                is_new, copy = copier.add(content)
                if copy is None:
                    copied_failures.append(content)
                else:
                    copied_success.append(copy)
                    if is_new:
                        self.add_to_listing(copy)

        with manager.mover() as mover:
            for identifier, content in self.get_selected_content('cutted'):
                is_new, moved_content = mover.add(content)
                if moved_content is None:
                    moved_failures.append(content)
                else:
                    moved_success.append(moved_content)
                    if is_new:
                        self.add_to_listing(moved_content)

        # Notifications
        if copied_success:
            if copied_failures:
                self.notify(
                    _(u'Pasted as a copy ${copied} but could not copy ${not_copied}.',
                      mapping={'copied': copied_success,
                               'not_copied': copied_failures}))
            else:
                self.notify(
                    _(u'Pasted as a copy ${copied}.',
                      mapping={'copied': copied_success}))
        elif copied_failures:
            self.notify(
                _(u'Could not copy ${not_copied}.',
                  mapping={'not_copied': copied_failures}))
        if moved_success:
            if moved_failures:
                self.notify(
                    _(u"Moved ${moved} but could not move ${not_moved}.",
                      mapping={'moved': moved_success,
                               'not_moved': moved_failures}))
            else:
                self.notify(
                    _(u'Moved ${moved}.',
                      mapping={'moved': moved_success}))
        elif moved_failures:
            self.notify(
                _(u'Could not move ${not_moved}.',
                  mapping={'not_moved': moved_failures}))

        return {}


class PasteAsGhostActionREST(ActionREST):
    grok.name('silva.ui.listing.pasteasghost')

    def payload(self):
        success = ContentCounter(self)
        failures = ContentCounter(self)

        manager = IContainerManager(self.context)

        with manager.ghoster() as ghoster:
            for identifier, content in self.get_selected_content('copied'):
                ghost = ghoster.add(content)
                if ghost is None:
                    failures.append(content)
                else:
                    success.append(ghost)
                    self.add_to_listing(ghost)

        # Notifications
        if success:
            if failures:
                self.notify(
                    _(u"Created ghost for ${ghosted} but could do it for ${not_ghosted}",
                      mapping={'ghosted': success,
                               'not_ghosted': failures}))
            else:
                self.notify(
                    _(u"Created ghost for ${ghosted}.",
                      mapping={'ghosted': success}))
        elif failures:
            self.notify(
                _(u"Could not create ghost for ${not_ghosted}.",
                  mapping={'not_ghosted': failures}))
        return {}


class RenameActionREST(ActionREST):
    grok.name('silva.ui.listing.rename')

    def payload(self):
        success = ContentCounter(self)
        failures = ContentCounter(self)

        manager = IContainerManager(self.context)

        form = self.request.form
        total = int(form.get('values', 0))
        get_content = getUtility(IIntIds).getObject

        with manager.renamer() as renamer:
            for position in range(total):
                id = int(form['values.%d.id' % position])
                content = get_content(id)
                identifier = form['values.%d.identifier' % position]
                title = form['values.%d.title' % position]
                renamed_content = renamer.add((content, identifier, title))
                if renamed_content is None:
                    failures.append(content)
                else:
                    success.append(renamed_content)
                    self.remove_from_listing(id)
                    self.add_to_listing(renamed_content)

        # Notifications
        if success:
            if failures:
                self.notify(
                    _(u'Renamed ${renamed}, but could not rename ${not_renamed}.',
                      mapping={'renamed': success,
                               'not_renamed': failures}))
            else:
                self.notify(
                    _(u'Renamed ${renamed}.',
                      mapping={'renamed': success}))
        elif failures:
            self.notify(
                _(u'Could not rename ${not_renamed}.',
                  mapping={'not_renamed': failures}))

        return {}


class PublishActionREST(ActionREST):
    grok.name('silva.ui.listing.publish')

    def payload(self):
        success = ContentCounter(self)
        failures = ContentCounter(self)

        for identifier, content in self.get_selected_content(recursive=True):
            workflow = IPublicationWorkflow(content, None)
            if workflow is not None:
                try:
                    workflow.publish()
                except PublicationWorkflowError:
                    failures.append(content)
                else:
                    if identifier is not None:
                        self.update_in_listing(content)
                    success.append(content)
            else:
                failures.append(content)

        # Notifications
        if success:
            if failures:
                self.notify(
                    _(u'Published ${published}, but could not publish ${not_published}.',
                      mapping={'published': success,
                               'not_published': failures}))
            else:
                self.notify(
                    _(u'Published ${published}.',
                      mapping={'published': success}))
        elif failures:
            self.notify(
                _(u'Could not publish ${not_published}.',
                  mapping={'not_published': failures}))

        return {}


class CloseActionREST(ActionREST):
    grok.name('silva.ui.listing.close')

    def payload(self):
        success = ContentCounter(self)
        failures = ContentCounter(self)

        for identifier, content in self.get_selected_content(recursive=True):
            workflow = IPublicationWorkflow(content, None)
            if workflow is not None:
                try:
                    workflow.close()
                except PublicationWorkflowError:
                    failures.append(content)
                else:
                    if identifier is not None:
                        self.update_in_listing(content)
                    success.append(content)
            else:
                failures.append(content)

        # Notifications
        if success:
            if failures:
                self.notify(
                    _(u'Closed ${closed}, but could not close ${not_closed}.',
                      mapping={'closed': success,
                               'not_closed': failures}))
            else:
                self.notify(
                    _(u'Closed ${closed}.',
                      mapping={'closed': success}))
        elif failures:
            self.notify(
                _(u'Could not close ${not_closed}.',
                  mapping={'not_closed': failures}))

        return {}


class NewVersionActionREST(ActionREST):
    grok.name('silva.ui.listing.newversion')

    def payload(self):
        success = ContentCounter(self)
        failures = ContentCounter(self)

        for ignored, content in self.get_selected_content():
            workflow = IPublicationWorkflow(content, None)
            if workflow is not None:
                try:
                    workflow.new_version()
                except PublicationWorkflowError:
                    failures.append(content)
                else:
                    self.update_in_listing(content)
                    success.append(content)
            else:
                failures.append(content)

        # Notifications
        if success:
            if failures:
                self.notify(
                    _(u'New version(s) created for ${newversion}, '
                      u'but could do it for ${not_newversion}.',
                      mapping={'newversion': success,
                               'not_newversion': failures}))
            else:
                self.notify(
                    _(u'New version(s) created for ${newversion}.',
                      mapping={'newversion': success}))
        elif failures:
            self.notify(
                _(u'Could not create new version(s) for ${not_newversion}.',
                  mapping={'not_newversion': failures}))

        return {}


class Order(UIREST):
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
            status = 'success'
            self.notify(
                _(u'Content moved in position ${position}',
                  mapping={'position': position + 1}),
                type='feedback')
        else:
            status = 'failure'
            self.notify(
                _(u'Could not move content in position ${position}',
                  mapping={'position': position + 1}),
                type='error')

        return self.json_response({
                'status': status, 'notifications': self.get_notifications()})
