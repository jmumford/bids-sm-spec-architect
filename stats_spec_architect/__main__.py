from stats_spec_architect.layout_loading import LayoutLoadWindow
from stats_spec_architect.main_gui import launch_main_gui


def main():
    initial_window = LayoutLoadWindow(
        on_data_loaded=launch_main_gui, themename='superhero', minsize=(300, 150)
    )
    initial_window.mainloop()


if __name__ == '__main__':
    main()
