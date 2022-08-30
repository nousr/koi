from krita import DockWidgetFactory, DockWidgetFactoryBase
from .koi import Koi

DOCKER_ID = "koi"

instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID, DockWidgetFactoryBase.DockRight, Koi)

instance.addDockWidgetFactory(dock_widget_factory)
