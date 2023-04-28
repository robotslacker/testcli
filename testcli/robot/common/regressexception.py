# -*- coding: utf-8 -*-

class RegressException(Exception):
    def __init__(self, message, inner_exception=None):
        Exception.__init__(self)
        self.message = message
        self.inner_exception = inner_exception

    def __str__(self):
        return self.message
