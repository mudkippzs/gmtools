class AppState:
    def __init__(self):
        self.selected_category = None
        self.selected_type = None
        self.num_results = 3
        self.contexts = []
        self.min_level = 1
        self.max_level = 3
        self.regenerate_name_only = False
        self.lock_name = False
        self.last_results = []
        self.detail_display_mode = "Plain Text"
        self.campaign_prompt = ""
        self.system = ""
        self.setting = ""
