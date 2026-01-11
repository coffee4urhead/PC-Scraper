class GUIStateManager:
    def __init__(self, master):
        self.master = master
    
    def capture_current_state(self):
        """Capture all current user inputs and selections"""
        state = {}
        
        if hasattr(self.master, 'left_entry'):
            state['search_text'] = self.master.left_entry.get()
        
        if hasattr(self.master, 'left_part_select'):
            state['selected_part'] = self.master.left_part_select.get()
        
        if hasattr(self.master, 'left_website_select'):
            state['selected_website'] = self.master.left_website_select.get()
        
        return state
    
    def restore_state(self, state):
        """Restore user inputs and selections"""
        if 'search_text' in state and hasattr(self.master, 'left_entry'):
            self.master.left_entry.insert(0, state['search_text'])
        
        if 'selected_part' in state and hasattr(self.master, 'left_part_select'):
            self.master.left_part_select.set(state['selected_part'])
        
        if 'selected_website' in state and hasattr(self.master, 'left_website_select'):
            self.master.left_website_select.set(state['selected_website'])