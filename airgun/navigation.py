"""AirGun's implementation of base navigation and navigate steps."""
from cached_property import cached_property
import navmazing
from selenium.common.exceptions import NoSuchElementException


class NavigateStep(navmazing.NavigateStep):
    """AirGun's version of :class:`navmazing.NavigateStep` with custom
    implementations of `navmazing.NavigateStep.am_i_here` and `navmazing.NavigateStep.go`
    and ability to work with views.
    """

    VIEW = None

    def __init__(self, obj, navigate_obj, logger=None):
        """Adding shortcut for navigate object to make easier calls to its
        navigate method
        """
        super().__init__(obj, navigate_obj, logger=logger)
        self.navigate_to = self.navigate_obj.navigate

    @cached_property
    def view(self):
        """Cached property which returns instance of view, which was defined
        for current navigate step by ``VIEW`` class attribute.
        """
        if self.VIEW is None:
            raise AttributeError(f'{type(self).__name__} does not have VIEW specified')
        return self.create_view(self.VIEW, additional_context={'entity': self.obj})

    def create_view(self, view_class, additional_context=None):
        """Method which creates an instance of view, defined by ``view_class``.

        Created instance will have references to ``entity``,
        :class:`airgun.browser.AirgunBrowser` and
        :class:`airgun.session.Session` set as instance attributes
        ``self.context['entity']``, ``self.browser`` and ``self.extra.session``
        correspondingly.

        :param widgetastic.widget.View view_class: class of view to create
        :param dict optional additional_context: any additional context you
            want to include. ``entity`` is set to current navigate step entity
            by default
        :return: instance of view
        :rtype: widgetastic.widget.View
        """
        if additional_context is None:
            additional_context = {}
        if not additional_context.get('entity'):
            additional_context['entity'] = self.obj
        return view_class(self.navigate_obj.browser, additional_context=additional_context)

    def am_i_here(self, *args, **kwargs):
        """Describes if the navigation is already at the requested destination.

        By default, airgun relies on view's ``is_displayed`` property to
        determine whether navigation succeeded. If positional argument
        ``entity_name`` was passed and view has ``BreadCrumb`` widget, it will
        also ensure second location in breadcrumb is provided entity name.

        This method may be overridden on specific entity's NavigateStep level
        for more complex logic if needed.

        :return: whether navigator is at requested destination or not.
        :rtype: bool
        """
        entity_name = kwargs.get('entity_name')
        try:
            if entity_name and hasattr(self.view, 'breadcrumb'):
                return self.view.is_displayed and self.view.breadcrumb.locations[1] in (
                    entity_name,
                    f'Edit {entity_name}',
                )
            return self.view.is_displayed
        except (AttributeError, NoSuchElementException):
            return False

    def go(self, _tries=0, *args, **kwargs):
        """Wrapper around :meth:`navmazing.NavigateStep.go` which returns
        instance of view after successful navigation flow.

        :return: view instance if class attribute ``VIEW`` is set or ``None``
            otherwise
        """
        super().go(*args, _tries=_tries, **kwargs)
        view = self.view if self.VIEW is not None else None
        return view


class Navigate(navmazing.Navigate):
    """Wrapper around :class:`navmazing.Navigate` which adds airgun browser as
    class attribute.

    For more information about :class:`Navigate` please refer to
    `navmazing docs <https://github.com/RedHatQE/navmazing>`_.
    """

    def __init__(self, browser=None):
        """Store airgun browser instance to be able to perform navigation
        steps.

        :param airgun.browser.AirgunBrowser browser: airgun browser instance to
            perform navigation with
        """
        super().__init__()
        self.browser = browser


# Navigator instance to be used in other modules. Please note that you should
# use it only for registering navigation steps, not for actual navigation. For
# navigation use :attr:`airgun.Session.navigate_to` instead.
navigator = Navigate()
