# -*- coding: utf-8 -*-
import pytest


@pytest.mark.skip
def test1():
    assert 1 == 1


def test2():
    assert 1 == 1


def test3():
    assert 2 == 1
