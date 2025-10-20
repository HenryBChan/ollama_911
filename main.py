import multiprocessing

def main():
    from src import AI_911_operator
    from src import AI_911_gui

    print ("main: start")

    p1 = multiprocessing.Process(target=AI_911_gui.gui_main)
    p2 = multiprocessing.Process(target=AI_911_operator.operator_main)

    p1.start()
    p2.start()

    # Wait for GUI to close
    p1.join()
    p2.terminate()

if __name__ == "__main__":
    main()