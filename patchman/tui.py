import pytermgui as ptg
from pytermgui import boxes, HorizontalAlignment

ptg.KeyboardButton.parent_align = HorizontalAlignment.LEFT
ptg.KeyboardButton.styles.label = ""


class PatchButton(ptg.KeyboardButton):
    def __init__(self, i, dir, on_select):
        self.dir = dir
        super().__init__(f"{i+1} {dir}", on_select, bound=str(i+1))


class PatchTUI:
    def __init__(self):
        self.selected_patch = None

    def select_patch(self, patches):
        button_container = ptg.Container(
            *self._buttons(patches), box=boxes.EMPTY)
        container = ptg.Container(
            self._search_input(patches, button_container),
            button_container,
            box=boxes.EMPTY,
            parent_align=HorizontalAlignment.LEFT
        )
        container.select(0)
        ptg.inline(container)

        if not self.selected_patch:
            if type(container.selected) is PatchButton:
                self.selected_patch = container.selected.dir

        return self.selected_patch

    def _search_input(self, dirs, button_container: ptg.Container):
        field = ptg.InputField(prompt="> ")

        def update(key):
            if key == ptg.keys.BACKSPACE:
                field.delete_back()

            button_container.set_widgets(
                self._buttons(dirs, field.value)
            )

        field.bind(ptg.keys.ANY_KEY, lambda _, key: update(key))
        field.bind(ptg.keys.BACKSPACE, lambda _, key: update(key))
        return field

    def _buttons(self, dirs, filter=""):
        return [
            PatchButton(i, dir, self._on_select(dir))
            for i, dir in enumerate(dirs)
            if not filter or filter in str(dir)
        ]

    def _on_select(self, p):
        def on_select(btn):
            self.selected_patch = p
            ptg.WindowManager().stop()
        return on_select
