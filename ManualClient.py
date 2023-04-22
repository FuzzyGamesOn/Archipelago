from __future__ import annotations
from worlds import AutoWorldRegister

import asyncio

import ModuleUpdate
ModuleUpdate.update()

import Utils

if __name__ == "__main__":
    Utils.init_logging("ManualClient", exception_logger="Client")

from NetUtils import ClientStatus
from CommonClient import gui_enabled, logger, get_base_parser, ClientCommandProcessor, \
    CommonContext, server_loop


class ManualClientCommandProcessor(ClientCommandProcessor):
    def _cmd_resync(self):
        """Manually trigger a resync."""
        self.output(f"Syncing items.")
        self.ctx.syncing = True


class ManualContext(CommonContext):
    command_processor: int = ManualClientCommandProcessor
    game = "not set" # this is changed in server_auth below based on user input
    items_handling = 0b111  # full remote

    def __init__(self, server_address, password):
        super(ManualContext, self).__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = False
        self.awaiting_bridge = False
        
    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(ManualContext, self).server_auth(password_requested)

        self.game = "Manual"

        self.location_names_to_id = dict([(value, key) for key, value in self.location_names.items()])

        # if the item name has a number after it, remove it
        for item_id, name in enumerate(self.item_names):
            if not isinstance(name, str):
                continue

            name_parts = name.split(":")

            if len(name_parts) > 1:
                self.item_names.pop(name)
                self.item_names[name_parts[0]] = item_id

        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(ManualContext, self).connection_closed()

    @property
    def endpoints(self):
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super(ManualContext, self).shutdown()

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected", "ReceivedItems", "RoomUpdate"}:
            self.ui.build_tracker_and_locations_table() # rebuild the item and location list after receiving an update to either

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager
        
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.layout import Layout
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.textinput import TextInput
        from kivy.uix.tabbedpanel import TabbedPanelItem
        from kivy.clock import Clock

        class TrackerAndLocationsLayout(GridLayout):
            pass
    
        class TrackerLayoutScrollable(ScrollView):
            pass

        class TrackerLayout(GridLayout):
            pass

        class LocationsLayoutScrollable(ScrollView):
            pass

        class LocationsLayout(GridLayout):
            pass

        class ManualManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago"),
                ("Manual", "Manual"),
            ]
            base_title = "Archipelago Manual Client"

            ctx: ManualContext

            def __init__(self, ctx):
                super().__init__(ctx)

            def build(self) -> Layout:
                super(ManualManager, self).build()
                #
                self.manual_game_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)

                panel = TabbedPanelItem(text="Tracker and Locations", size_hint_y = 1)
                self.tracker_and_locations_panel = panel.content = TrackerAndLocationsLayout(cols = 2)

                self.tabs.add_widget(panel)

                self.build_tracker_and_locations_table()

                return self.container
            
            def build_tracker_and_locations_table(self):
                self.tracker_and_locations_panel.clear_widgets()

                if not self.ctx.server or not self.ctx.auth:
                    self.tracker_and_locations_panel.add_widget(
                                Label(text="Waiting for connection...", size_hint_y=None, height=50, outline_width=1))
                    return

                items_length = len(self.ctx.items_received)
                tracker_panel_scrollable = TrackerLayoutScrollable()
                tracker_panel = TrackerLayout(cols = 1, size_hint = (None, None))
                tracker_panel.bind(minimum_height = tracker_panel.setter('height'))
                self.tracker_and_locations_panel.add_widget(
                                Label(text="Items Received (%d)" % (items_length), size_hint_y=None, height=50, outline_width=1))
                
                listed_items = set()

                for network_item in self.ctx.items_received: 
                    if (network_item.item not in listed_items):
                        item_name_parts = self.ctx.item_names[network_item.item].split(":")
                        
                        item_count = len(list(item for item in self.ctx.items_received if item.item == network_item.item))
                        item_text = Label(text="%s (%s)" % (item_name_parts[0], item_count), size_hint=(None, None), height=30, width=400)
                        tracker_panel.add_widget(item_text)

                        listed_items.add(network_item.item)

                locations_length = len(self.ctx.missing_locations)
                locations_panel_scrollable = LocationsLayoutScrollable()
                locations_panel = LocationsLayout(cols = 1, size_hint = (None, None))
                locations_panel.bind(minimum_height = locations_panel.setter('height'))
                self.tracker_and_locations_panel.add_widget(
                                Label(text="Remaining Locations (%d)" % (locations_length + 1), size_hint_y=None, height=50, outline_width=1))
                
                for location_id in self.ctx.missing_locations:
                    location_button = Button(text=self.ctx.location_names[location_id], size_hint=(None, None), height=30, width=400)
                    location_button.bind(on_press=self.location_button_callback)
                    locations_panel.add_widget(location_button)

                # Add the Victory location to be marked at any point, which is why locations length has 1 added to it above
                location_button = Button(text="VICTORY! (seed finished)", size_hint=(None, None), height=30, width=400)
                location_button.bind(on_press=self.victory_button_callback)
                locations_panel.add_widget(location_button)
                
                tracker_panel_scrollable.add_widget(tracker_panel)
                locations_panel_scrollable.add_widget(locations_panel)
                self.tracker_and_locations_panel.add_widget(tracker_panel_scrollable)
                self.tracker_and_locations_panel.add_widget(locations_panel_scrollable)
                    
            def location_button_callback(self, button):
                # location_id = AutoWorldRegister.world_types[self.ctx.game].location_name_to_id[button.text];
                location_id = self.ctx.location_names_to_id[button.text]

                if location_id:
                    self.ctx.locations_checked.append(location_id)
                    self.ctx.syncing = True

                    # message = [{"cmd": 'LocationChecks', "locations": [location_id]}]
                    # self.ctx.send_msgs(message)

            def victory_button_callback(self, button):
                self.ctx.items_received.append("__Victory__")
                self.ctx.syncing = True

        self.ui = ManualManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

async def game_watcher(ctx: ManualContext):
    while not ctx.exit_event.is_set():
        if ctx.syncing == True:
            sync_msg = [{'cmd': 'Sync'}]
            if ctx.locations_checked:
                sync_msg.append({"cmd": "LocationChecks", "locations": list(ctx.locations_checked)})
            await ctx.send_msgs(sync_msg)
            ctx.syncing = False
        sending = []
        victory = ("__Victory__" in ctx.items_received)
        ctx.locations_checked = sending
        message = [{"cmd": 'LocationChecks', "locations": sending}]
        await ctx.send_msgs(message)
        if not ctx.finished_game and victory:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    async def main(args):
        ctx = ManualContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        progression_watcher = asyncio.create_task(
            game_watcher(ctx), name="ManualProgressionWatcher")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await progression_watcher

        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Manual Client, for operating a Manual game in Archipelago.")

    args, rest = parser.parse_known_args()
    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
