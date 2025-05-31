from typing import Optional
import pytermgui as ptg
from pytermgui import boxes, HorizontalAlignment
from patchman.manager import PatchManager
import time

# Set default alignment and style for all KeyboardButtons
ptg.KeyboardButton.parent_align = HorizontalAlignment.LEFT
ptg.KeyboardButton.styles.label = ""

def clear():
    ptg.clear()
    ptg.reset()
    ptg.move_cursor((0,0))

class ForwardingWindow(ptg.Window):
    """A Window that forwards key bindings to its content."""
    def __init__(self, content, **kwargs):
        super().__init__(content, **kwargs)
        self.content = content

    def execute_binding(self, key, **kwargs):
        """Forward key bindings to content if not handled by window."""
        if super().execute_binding(key, **kwargs):
            return True
        return self.content.execute_binding(key, **kwargs)

class PatchButton(ptg.Container):
    """A container for a patch entry, with actions for apply, revert, view, rename, and delete."""
    def __init__(self, i: int, dir: str, on_select):
        self.index = i + 1
        self.dir = dir
        self.on_select = on_select
        super().__init__(
            self._btn(),
            box=boxes.EMPTY,
            parent_align=HorizontalAlignment.LEFT
        )
    
    @property
    def value(self) -> str:
        """Display value for the button (index and patch name)."""
        return f"{self.index} {self.dir}"

    @property
    def confirmation_message(self) -> str:
        """Message to show when confirming deletion."""
        return f"Delete {self.dir} (y/n): "

    def _btn(self) -> ptg.KeyboardButton:
        """Create the KeyboardButton for this patch."""
        return ptg.KeyboardButton(self.value, self.on_select, bound=str(self.index))

    def _reset(self):
        return lambda _, __: (self.set_widgets([self._btn()]), self.select(0))

    def _create_input_field(self, prompt: str, value: str, on_enter = None, on_exit = None) -> ptg.InputField:
        """Create an input field with given prompt and value."""
        on_enter = on_enter or self._reset()
        on_exit = on_exit or self._reset()
        inp = ptg.InputField(prompt=prompt, value=value)
        inp.bind(ptg.keys.ENTER, on_enter)
        inp.bind(ptg.keys.ESC, on_exit)
        return inp

    def action_with_callback(self, action: str, callback=None):
        """Execute an action with an optional callback."""
        method = getattr(self, action)
        if callback:
            method(callback)
        else:
            method()

    def apply(self):
        """Apply the patch and exit the TUI."""
        ptg.WindowManager().stop()
        PatchManager().apply(self.dir)

    def revert(self):
        """Revert the patch and exit the TUI."""
        ptg.WindowManager().stop()
        PatchManager().apply(self.dir, True)

    def view(self):
        """Show the diff for this patch and exit the TUI."""
        PatchManager().diff(self.dir)
        clear()

    def edit(self):
        """Open the patch in vim for editing and exit the TUI."""
        PatchManager().edit(self.dir)
        clear()

    def rename(self):
        """Show an input field to rename the patch."""
        clear()
        inp = self._create_input_field("Rename: ", self.dir, lambda _, __: self._rename(inp.value))
        self.set_widgets([inp])
        self.select(0)

    def delete(self, cb):
        """Show an input field to confirm deletion."""
        inp = self._create_input_field("", self.confirmation_message)
        inp.bind("y", lambda _, __: self._delete(cb))
        inp.bind("n", self._reset())
        self.set_widgets([inp])
        self.select(0)
        clear()

    def _rename(self, value):
        """Perform the rename operation and update the button."""
        if value:
            PatchManager().rename(self.dir, value)
            self.dir = value
        self.set_widgets([self._btn()])

    def _delete(self, cb):
        """Delete the patch and notify the container."""
        PatchManager().delete(self.dir)
        self.set_widgets([])
        cb(self)  # Callback to remove the button from the container


class PatchButtonContainer(ptg.Container):
    """Container for PatchButton widgets, with filtering and removal support."""
    def __init__(self, on_select=lambda _: None, **attrs):
        super().__init__(**attrs)
        self.selected_index = 0
        self.on_select = on_select
        self.filter("")
    
    @property
    def dirs(self) -> list[str]:
        """List of patch directories."""
        return PatchManager().list()

    def get_button(self, kb_button) -> Optional[PatchButton]:
        """Get the PatchButton instance for a given KeyboardButton."""
        return next(
            (w for w in self._widgets 
             if hasattr(w, "rename") and getattr(w, "_widgets", [None])[0] is kb_button),
            None
        )

    def filter(self, filter_text: str) -> None:
        """Filter patch buttons by text."""
        filtered_buttons = [
            PatchButton(i, dir, self.on_select)
            for i, dir in enumerate(self.dirs)
            if filter_text.lower() in dir.lower()
        ]
        self.set_widgets(filtered_buttons)

    def remove(self, button: PatchButton) -> None:
        """Remove a PatchButton from the container and update the list."""
        if button in self._widgets:
            self._widgets.remove(button)
        self.filter("")


class SearchInput(ptg.InputField):
    """Custom input field for searching patches."""
    def __init__(self, prompt, data: PatchButtonContainer, **kwargs):
        super().__init__(**kwargs)
        self._data = data
        self._prompt = prompt
        self._enabled = False

    def _update(self, key):
        if key == ptg.keys.BACKSPACE:
            self.delete_back()
        self._data.filter(self.value)
    
    @property
    def selectables_length(self) -> int:
        return int(self._enabled)
    
    def enable(self): 
        self._enabled = True
        self.prompt = self._prompt
        self.bind(ptg.keys.ANY_KEY, lambda _, key: self._update(key))
        self.bind(ptg.keys.BACKSPACE, lambda _, key: self._update(key))

    def disable(self): 
        self._enabled = False
        if self.value == "":
            self.prompt = ""
        if ptg.keys.ANY_KEY in self.bindings: self.unbind(ptg.keys.ANY_KEY)
        if ptg.keys.BACKSPACE in self.bindings: self.unbind(ptg.keys.BACKSPACE)


class PatchTUI:
    """Main TUI class for patch management."""
    def __init__(self):
        self.selected_patch = None

    def _setup_key_bindings(self, container: ptg.Container, button_container: PatchButtonContainer, search: SearchInput):
        """Set up all key bindings for the TUI."""
        # Search and navigation bindings
        button_container.bind("s", lambda _, __: (search.enable(), container.select(0)))
        button_container.bind(":", lambda _, __: (search.enable(), container.select(0)))
        button_container.bind("q", lambda _, __: ptg.WindowManager().stop())

        # Patch action bindings with their callbacks
        actions = {
            "a": ("apply", None),
            "R": ("revert", None),
            "v": ("view", None),
            "e": ("edit", None),
            "r": ("rename", None),
            "d": ("delete", lambda btn: button_container.remove(btn))
        }
        
        # Bind each action with its optional callback
        for key, (action, callback) in actions.items():
            button_container.bind(key, lambda _, __, a=action, cb=callback: 
                self._execute_action(button_container, container, a, cb)
            )
        
        _s = container.select
        container.select = lambda index: (
            _s(index), search.disable() if index and index > 0 else None
        )

        # Escape from search
        search.bind(ptg.keys.ESC, lambda _, __: (container.select(container.selected_index + 1), search.disable()))

    def _execute_action(self, button_container: PatchButtonContainer, container: ptg.Container, action: str, cb=None):
        btn = button_container.get_button(container.selected)
        if btn:
            btn.action_with_callback(action, cb)

    def _create_shortcuts_panel(self):
        """Create the shortcuts panel with two columns."""
        shortcuts = ptg.Splitter(
            ptg.Container(
                ptg.Label("<s> Search", parent_align=HorizontalAlignment.LEFT),
                ptg.Label("<r> Rename", parent_align=HorizontalAlignment.LEFT),
                ptg.Label("<d> Delete", parent_align=HorizontalAlignment.LEFT),
                ptg.Label("<q> Quit", parent_align=HorizontalAlignment.LEFT),
                box=boxes.EMPTY,
                parent_align=HorizontalAlignment.CENTER,
            ),
            ptg.Container(
                ptg.Label("<e> Edit", parent_align=HorizontalAlignment.LEFT),
                ptg.Label("<a> Apply", parent_align=HorizontalAlignment.LEFT),
                ptg.Label("<R> Revert", parent_align=HorizontalAlignment.LEFT),
                ptg.Label("<v> View", parent_align=HorizontalAlignment.LEFT),
                box=boxes.EMPTY,
                parent_align=HorizontalAlignment.CENTER
            ),
        )
        shortcuts.chars["separator"] = ""
        return shortcuts

    def manage(self):
        """
        Main patch management UI. Displays shortcuts, search, and patch list.
        """
        # Create UI components
        shortcuts = self._create_shortcuts_panel()
        button_container = PatchButtonContainer(box=boxes.EMPTY)
        search = SearchInput("Search: ", button_container)

        # Main container layout
        container = ptg.Container(
            ptg.Container(shortcuts),
            search,
            button_container,
            box=boxes.EMPTY,
            parent_align=HorizontalAlignment.LEFT
        )

        container.select(0)  # Focus first element

        self._setup_key_bindings(container, button_container, search)

        # Run the TUI
        clear()
        ptg.inline(container, exit_on=[ptg.keys.CTRL_C])
        # with ptg.WindowManager() as manager:
        #     manager.layout.add_slot("Main")
        #     manager.add(w)
        #     manager.run()

    def select_patch(self, patches):
        """UI for selecting a patch only."""
        button_container = ptg.Container(
            *self._buttons(patches), box=boxes.EMPTY)

        search = SearchInput("Search: ", button_container)
        search.enable()

        container = ptg.Container(
            search,
            button_container,
            box=boxes.EMPTY,
            parent_align=HorizontalAlignment.LEFT
        )
        container.select(0)
        ptg.inline(container)

        if not self.selected_patch:
            if isinstance(container.selected, PatchButton):
                self.selected_patch = container.selected.dir

        return self.selected_patch

    def _buttons(self, dirs, filter=""):
        """Create PatchButton widgets for a list of patch dirs."""
        return [
            PatchButton(i, dir, self._on_select(dir))
            for i, dir in enumerate(dirs)
            if not filter or filter in str(dir)
        ]

    def _on_select(self, p):
        """Callback for selecting a patch."""
        def on_select(btn):
            self.selected_patch = p
            ptg.WindowManager().stop()
        return on_select
