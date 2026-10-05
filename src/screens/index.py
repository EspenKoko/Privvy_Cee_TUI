# from textual.screen import Screen
# from textual.widgets import Header, Footer, Label, TabPane, TabbedContent
# from textual.containers import Container, Vertical

# from src.screens.dashboard import DashboardScreen

# class Index(Screen):
    
#     def compose(self):
#         yield Header(show_clock=True)
#         with Container(id="dashboard-card"):
#             yield Label(f"Welcome — Server Dashboard", id="welcome")
#             with TabbedContent(initial="Dashboard"):
#                 with TabPane("Dashboard", id="Dashboard"):
#                     yield DashboardScreen()
#                 with TabPane("Activity Log", id="log-tab"):
#                     yield Label(f"Welcome", id="we")
#                     # yield ActivityLogTab()
#         yield Footer()
        