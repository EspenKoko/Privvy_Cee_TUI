from src.app import HomelabApp

# Expose `app` for `textual run --dev main` (it imports the name `app` from the module)
# `textual` accepts either an App subclass or factory; expose the class here.
app = HomelabApp

def main() -> None:
    instance = HomelabApp()
    instance.run()

if __name__ == "__main__":
    main()
