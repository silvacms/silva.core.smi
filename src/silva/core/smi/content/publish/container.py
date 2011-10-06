# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from infrae.comethods import comethod

from silva.core.interfaces import IContainer
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces.errors import VersioningError, PublicationError
from silva.core.smi.content.publish import IPublicationFields
from silva.translations import translate as _
from silva.ui.rest.container.generator import ContentGenerator
from silva.ui.rest.container.notifier import ContentNotifier

from zeam.form import autofields
from zeam.form.silva.interfaces import IDefaultAction
from zeam.form.silva.interfaces import IRESTCloseOnSuccessAction
from zeam.form.ztk.actions import EditAction
from zeam.form import silva as silvaforms


class MultiApproveAction(EditAction):
    grok.implements(IDefaultAction, IRESTCloseOnSuccessAction)
    title = _(u"Approve")

    @comethod
    def approver(self, form, data):
        content = yield
        while content is not None:
            result = None
            workflow = IPublicationWorkflow(content, None)
            if workflow is None:
                result = PublicationError(
                    _(u"This action is not applicable on this content."),
                    content)
            else:
                try:
                    self.applyData(form, form.dataManager(content), data)
                    IPublicationWorkflow(content).approve()
                except VersioningError as error:
                    result = error
                else:
                    result = content
            content = yield result

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE

        get_notifier = ContentNotifier(form.request)
        with self.approver(form, data) as approver:
            with get_notifier(
                approver,
                u"Approved for the future ${contents}.",
                u"Could not approve ${contents}: ${reason}") as notifier:
                with ContentGenerator(get_notifier.notify) as get_contents:
                    notifier.map(get_contents(
                            form.request.form.get('form.prefix.contents')))
        return silvaforms.SUCCESS



class ApproveForFuturePopupForm(silvaforms.RESTPopupForm):
    grok.context(IContainer)
    grok.name('silva.core.smi.approveforfuture')

    fields = autofields.FieldsCollector(IPublicationFields)
    dataManager = autofields.FieldsDataManager()
    actions = silvaforms.Actions(silvaforms.CancelAction(),
                                 MultiApproveAction(identifier='approve'))

    label = _('Approve content for future')
    description = _(u'Approve selected content for the future')
    ignoreContent = True
    ignoreRequest = False
