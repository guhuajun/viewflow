from viewflow.activation import AbstractGateActivation
from viewflow import base, mixins
from viewflow.token import Token
from viewflow.flow import views


class DynamicSplitActivation(AbstractGateActivation):
    def calculate_next(self):
        self._split_count = self.flow_task._task_count_callback(self.process)

    def activate_next(self):
        if self._split_count:
            token_source = Token.split_token_source(self.task.token, self.task.pk)
            for _ in range(self._split_count):
                self.flow_task._next.activate(prev_activation=self, token=next(token_source))


class DynamicSplit(mixins.TaskDescriptionMixin,
                   mixins.NextNodeMixin,
                   mixins.UndoViewMixin,
                   mixins.CancelViewMixin,
                   mixins.PerformViewMixin,
                   mixins.DetailsViewMixin,
                   base.Gateway):
    """
    Activates several outgoing task instances depends on callback value

    Example::

        spit_on_decision = flow.DynamicSplit(lambda p: 4) \\
            .Next(this.make_decision)

        make_decision = flow.View(MyView) \\
            .Next(this.join_on_decision)

        join_on_decision = flow.Join() \\
            .Next(this.end)
    """
    task_type = 'SPLIT'

    cancel_view_class = views.CancelView
    details_view_class = views.DetailsView
    perform_view_class = views.PerformView
    undo_view_class = views.UndoView

    activation_cls = DynamicSplitActivation

    def __init__(self, callback, **kwargs):
        super(DynamicSplit, self).__init__(**kwargs)
        self._task_count_callback = callback
