import pytermgui as ptg
import os
from pytermgui import boxes, HorizontalAlignment

ptg.KeyboardButton.parent_align = HorizontalAlignment.LEFT
ptg.KeyboardButton.styles.label = ""


def on_select(p):
    def select(t):
        ptg.WindowManager().stop()
        print(p)

    return select


def search_input(dirs, button_container: ptg.Container):
    field = ptg.InputField(prompt="> ")

    def update(key):
        if key == ptg.keys.BACKSPACE:
            field.delete_back()

        button_container.set_widgets(
            buttons(dirs, field.value)
        )

    field.bind(ptg.keys.ANY_KEY, lambda _, key: update(key))
    field.bind(ptg.keys.BACKSPACE, lambda _, key: update(key))
    return field


def buttons(dirs, filter=""):
    return [
        ptg.KeyboardButton(
            f"{i+1} {dir}", on_select(dir), bound=str(i+1))
        for i, dir in enumerate(dirs)
        if not filter or filter in str(dir)
    ] + [filter]


def main(argv: list[str] | None = None) -> None:
    dirs = os.listdir()
    button_container = ptg.Container(*buttons(dirs), box=boxes.EMPTY)
    container = ptg.Container(
        search_input(dirs, button_container),
        button_container,
        box=boxes.EMPTY,
        parent_align=HorizontalAlignment.LEFT
    )
    container.select(0)

    ptg.inline(container)


if __name__ == "__main__":
    main()
