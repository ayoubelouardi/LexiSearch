import sys
from lexisearch.app import DictionaryTUI

def main():
    app = DictionaryTUI()
    app.run()

if __name__ == "__main__":
    sys.exit(main())
