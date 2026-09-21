"""R2M 可對使用者說明的停止原因。英文訊息給指令列。"""


class R2MStop(Exception):
    def __init__(self, english_message):
        super().__init__(english_message)
        self.english_message = english_message
