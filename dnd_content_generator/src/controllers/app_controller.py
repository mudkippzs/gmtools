import asyncio
from PySide6.QtCore import QThread, Signal, QObject
from src.services.file_manager import FileManager
from src.services.gpt_service import GPTService
from src.controllers.data_controller import DataController
from src.models.state import AppState

class GenerationWorker(QObject):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, data_controller, content_type, context_str, n_results):
        super().__init__()
        self.data_controller = data_controller
        self.content_type = content_type
        self.context_str = context_str
        self.n_results = n_results

    def run(self):
        try:
            results = asyncio.run(self.data_controller.generate_content_async(
                self.content_type,
                self.context_str,
                self.n_results
            ))
            if results:
                self.finished.emit(results)
            else:
                self.error.emit("No results generated.")
        except Exception as e:
            self.error.emit(str(e))

class AppController:
    def __init__(self):
        self.file_manager = FileManager()
        config = self.file_manager.config
        self.state = AppState()
        self.gpt_service = GPTService()
        self.data_controller = DataController(self.gpt_service, self)
        self.categories = self.file_manager.load_categories()
        self.contexts = self.file_manager.load_contexts()

    def set_system(self, system):
        self.state.system = system

    def set_setting(self, setting):
        self.state.setting = setting

    def set_detail_display_mode(self, mode):
        self.state.detail_display_mode = mode

    def set_category(self, category):
        self.state.selected_category = category

    def set_type(self, content_type):
        self.state.selected_type = content_type

    def set_num_results(self, n):
        self.state.num_results = n

    def set_level_range(self, min_level, max_level):
        self.state.min_level = min_level
        self.state.max_level = max_level

    def set_contexts(self, contexts):
        self.state.contexts = contexts

    def set_regen_options(self, name_only, lock_name):
        self.state.regenerate_name_only = name_only
        self.state.lock_name = lock_name

    def set_campaign_prompt(self, text):
        self.state.campaign_prompt = text

    def set_categories_file(self, filename):
        if filename:
            self.file_manager.categories_file = f"src/resources/{filename}"
        else:
            # fallback if needed
            pass

    def set_contexts_file(self, filename):
        if filename:
            self.file_manager.contexts_file = f"src/resources/{filename}"
        else:
            # fallback if needed
            pass

    def reload_categories(self):
        self.categories = self.file_manager.load_categories()

    def reload_contexts(self):
        self.contexts = self.file_manager.load_contexts()

    def generate_content_async(self, on_finished, on_error):
        if not self.state.selected_category or not self.state.selected_type:
            on_error("Please select a category and type before generating.")
            return

        # Construct context string with grouping
        # Example: If multiple contexts share the same parent, group them.
        # For simplicity, here we just join them. In advanced usage, 
        # you would find siblings and group them by their parent.
        context_list = self.state.contexts
        context_str = ", ".join(context_list)
        context_str += f" for characters between level {self.state.min_level} and {self.state.max_level}"

        self.worker_thread = QThread()
        self.worker = GenerationWorker(
            self.data_controller,
            self.state.selected_type,
            context_str,
            self.state.num_results
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def get_full_statblock(self, base_content):
        context_str = ", ".join(self.state.contexts)
        context_str += f" for characters between level {self.state.min_level} and {self.state.max_level}"
        return self.data_controller.get_full_statblock(self.state.selected_type, context_str, base_content)

    def export_to_logs(self, detailed=False):
        category = self.state.selected_type or "results"
        if detailed:
            for content in self.state.last_results:
                json_str = self._to_json_str(content)
                self.file_manager.write_to_log_file(category, json_str, detailed=True)
        else:
            if self.state.last_results:
                keys = list(self.state.last_results[0].keys())
                lines = [",".join(keys)]
                for r in self.state.last_results:
                    row = [str(r.get(k, "")) for k in keys]
                    lines.append(",".join(row))
                csv_data = "\n".join(lines)
                self.file_manager.write_to_log_file(category, csv_data)

    def _to_json_str(self, data):
        import json
        return json.dumps(data, ensure_ascii=False, indent=2)
