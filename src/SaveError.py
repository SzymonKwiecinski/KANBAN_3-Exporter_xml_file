from datetime import datetime
import traceback
import os


class SaveError:
    """write error data to file.

    Attributes:
        file: absolute file path

    """
    def __init__(self, path_to_error_file: str) -> None:
        self.file = path_to_error_file

    def save(self, str_traceback: str) -> None:
        """Open file and write error data to it."""
        with open(self.file, 'a') as file:
            print('\n================{}================\n'.format(datetime.now()), file=file)
            print(str_traceback, file=file)

            # file.write('\n================{}================\n'.format(datetime.now()))

            # file.write(str_traceback)

    def get_file_name(self) -> str:
        """Return absolute path to error file"""
        return os.path.abspath(self.file)

