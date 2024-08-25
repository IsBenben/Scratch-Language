from error import Error, raise_error
from records import Record
from nodes import NodeVisitor, String
from utils import mc_command

class Interpreter(NodeVisitor):
    def __init__(self) -> None:
        self.record = Record()