
TITLE = "Minecraft Coop AI Experiment"

if __name__ == '__main__':
    # The imports need to be done here for Kivy to support Multiprocessing without automatically opening new windows.
    from kivy.app import App
    from kivy.core.window import Window
    from kivy.uix.screenmanager import ScreenManager, FadeTransition
    from ui.dashboard import DashboardScreen
    from ui.start import ConfigurationScreen

    Window.borderless = False
    Window.size = (400, 300)


    class StartApp(App):

        def build(self):
            self.title = TITLE
            screen_manager = ScreenManager(transition=FadeTransition())
            screen_manager.add_widget(ConfigurationScreen())
            screen_manager.add_widget(DashboardScreen())
            Window.bind(on_request_close=self.on_request_close)
            return screen_manager

        def on_request_close(self, *args):
            if self.root.current == "DashboardScreen":
                return self.root.current_screen.on_request_close()
            else:
                return False


    StartApp().run()