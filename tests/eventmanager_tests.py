import unittest

from jinja2 import Markup
from flask import Flask

from flask_plugins import PluginManager, EventManager, connect_event, \
    emit_event, iter_listeners


class EventManagerInitTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.plugin_manager = PluginManager(self.app)

    def test_event_manager_init_with_plugin_manager(self):
        self.assertIsInstance(self.plugin_manager._event_manager, EventManager)

    def test_event_manager_standalone(self):
        event_manager = EventManager(self.app)

        self.assertIsInstance(event_manager, EventManager)


class EventManagerTests(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

        self.plugin_manager = PluginManager(self.app)
        self.event_manager = self.plugin_manager._event_manager

    def cb(self):
        return "Fred"

    def cb_before(self):
        pass

    def test_event_manager_connect(self):
        # first connect a callback, than register a callback on before the
        # last registered callback
        self.event_manager.connect('test-event', self.cb)                   # 3
        self.event_manager.connect('test-event', self.cb_before, 'before')  # 1
        self.event_manager.connect('test-event', self.cb, 'after')          # 4

        events = [event for event in self.event_manager.iter('test-event')]
        self.assertEquals(events[0], self.cb_before)
        self.assertEquals(events[2], self.cb)

    def test_event_manager_iter(self):
        no_events = [event for event in self.event_manager.iter('test-event')]

        self.assertEquals(len(no_events), 0)

        self.event_manager.connect('test-event', self.cb)

        events = [event for event in self.event_manager.iter('test-event')]
        self.assertEquals(len(events), 1)

    def test_event_manager_remove(self):
        self.event_manager.connect('test-event', self.cb)

        events = [event for event in self.event_manager.iter('test-event')]
        self.assertEquals(len(events), 1)

        # Test if a event is passed which didn't exist
        self.event_manager.remove('wrong-event', self.cb)
        self.assertEquals(len(events), 1)

        # Test if a callback is passed which didn't exist in the event
        self.event_manager.remove('test-event', self.cb_before)
        self.assertEquals(len(events), 1)

        # Test if it actually works
        self.event_manager.remove('test-event', self.cb)

        events = [event for event in self.event_manager.iter('test-event')]
        self.assertEquals(len(events), 0)

    def test_event_manager_template_emit(self):
        self.event_manager.connect('test-event', self.cb)

        self.assertIsInstance(
            self.event_manager.template_emit('test-event'), Markup
        )


class EventManagerHelpersTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

        self.plugin_manager = PluginManager(self.app)
        self.event_manager = self.plugin_manager._event_manager

    def callback(self):
        return "Fred"

    def test_helper_methods(self):
        with self.app.test_request_context():
            connect_event('test-event', self.callback)
            events = [event for event in iter_listeners('test-event')]
            emit_result = emit_event('test-event')

        self.assertEquals(len(events), 1)
        self.assertEquals(emit_result, ["Fred"])
