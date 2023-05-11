# -*- coding: utf-8 -*-
import sys
from os import linesep, path
from collections.abc import Sequence, Iterator, Callable
from .tokenizer import tokenize


def _html_escape(string):
    """
        功能: Html转码
        参数：
             string: 字符串
        返回：
            转码后的字符串

        HTML escape all of these " & < >

    """

    html_codes = {
        '"': '&quot;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
    }

    # & must be handled first
    string = string.replace('&', '&amp;')
    for char in html_codes:
        string = string.replace(char, html_codes[char])
    return string


def _get_key(key, scopes, warn, keep, def_ldel, def_rdel):
    """
        功能: 查找变量
        参数：
            key: 名称
            scopes: 范围
            warn: 是否输出警告信息
            keep: 是否返回
            def_ldel: 变量名左侧标识符
            def_rdel: 变量名右侧标识符
        返回：

    """
    """Get a key from the current scope"""

    # If the key is a dot
    if key == '.':
        # Then just return the current scope
        return scopes[0]

    # Loop through the scopes
    for scope in scopes:
        try:
            # For every dot seperated key
            for child in key.split('.'):
                # Move into the scope
                try:
                    # Try subscripting (Normal dictionaries)
                    scope = scope[child]
                except (TypeError, AttributeError):
                    try:
                        scope = getattr(scope, child)
                    except (TypeError, AttributeError):
                        # Try as a list
                        scope = scope[int(child)]

            # Return an empty string if falsy, with two exceptions
            # 0 should return 0, and False should return False
            if scope in (0, False):
                return scope

            try:
                if scope._CHEVRON_return_scope_when_falsy:
                    return scope
            except AttributeError:
                return scope or ''
        except (AttributeError, KeyError, IndexError, ValueError):
            # We couldn't find the key in the current scope
            # We'll try again on the next pass
            pass

    # We couldn't find the key in any of the scopes

    if warn:
        sys.stderr.write("Could not find key '%s'%s" % (key, linesep))

    if keep:
        return "%s %s %s" % (def_ldel, key, def_rdel)

    return ''


def _get_partial(name, partials_dict, partials_path, partials_ext):
    """
        功能: 加载子模板
        参数：
             name: 子模版名称
             partials_path: 子模板路径
             partials_ext: 子模版扩展名
             partials_dict: 子模版数据集
        返回：
            子模板
    """
    """Load a partial"""
    try:
        # Maybe the partial is in the dictionary
        return partials_dict[name]
    except KeyError:
        # Don't try loading from the file system if the partials_path is None or empty
        if partials_path is None or partials_path == '':
            return ''

        # Nope...
        try:
            # Maybe it's in the file system
            path_ext = ('.' + partials_ext if partials_ext else '')
            partial_path = path.join(partials_path, name + path_ext)
            with open(partial_path, 'r', encoding='utf-8') as partial:
                return partial.read()

        except IOError:
            # Alright I give up on you
            return ''


#
# The main rendering function
#
g_token_cache = {}


def render(template='', data={}, partials_path='.', partials_ext='html',
           partials_dict={}, padding='', def_ldel='{{', def_rdel='}}',
           scopes=None, warn=False, keep=False):
    """
        功能: 根据模板和数据集生成Html片段
        参数：
             template: 模板
             data: 数据集
             partials_path: 子模板路径
             partials_ext: 子模版扩展名
             partials_dict: 子模版数据集
             padding: 常量补丁
             def_ldel: 变量名左则符合
             def_rdel: 变量名右则符合
             scopes: 范围
             warn: 是否输出变量名警告信息
             keep: 是否返回变量名串
        返回：
            生成的Html片段
    """

    # If the template is a seqeuence but not derived from a string
    if isinstance(template, Sequence) and \
            not isinstance(template, str):
        # Then we don't need to tokenize it
        # But it does need to be a generator
        tokens = (token for token in template)
    else:
        if template in g_token_cache:
            tokens = (token for token in g_token_cache[template])
        else:
            # Otherwise make a generator
            tokens = tokenize(template, def_ldel, def_rdel)

    output = ""

    if scopes is None:
        scopes = [data]

    # Run through the tokens
    for tag, key in tokens:
        # Set the current scope
        current_scope = scopes[0]

        # If we're an end tag
        if tag == 'end':
            # Pop out of the latest scope
            del scopes[0]

        # If the current scope is falsy and not the only scope
        elif not current_scope and len(scopes) != 1:
            if tag in ['section', 'inverted section']:
                # Set the most recent scope to a falsy value
                # (I heard False is a good one)
                scopes.insert(0, False)

        # If we're a literal tag
        elif tag == 'literal':
            output += key.replace('\n', '\n' + padding)

        # If we're a variable tag
        elif tag == 'variable':
            # Add the html escaped key to the output
            thing = _get_key(key, scopes, warn=warn, keep=keep, def_ldel=def_ldel, def_rdel=def_rdel)
            if thing is True and key == '.':
                # if we've coerced into a boolean by accident
                # (inverted tags do this)
                # then get the un-coerced object (next in the stack)
                thing = scopes[1]
            output += _html_escape(thing)

        # If we're a no html escape tag
        elif tag == 'no escape':
            # Just lookup the key and add it
            thing = _get_key(key, scopes, warn=warn, keep=keep, def_ldel=def_ldel, def_rdel=def_rdel)
            output += thing

        # If we're a section tag
        elif tag == 'section':
            # Get the sections scope
            scope = _get_key(key, scopes, warn=warn, keep=keep, def_ldel=def_ldel, def_rdel=def_rdel)

            if isinstance(scope, Callable):

                # Generate template text from tags
                text = ''
                tags = []
                for tag in tokens:
                    if tag == ('end', key):
                        break

                    tags.append(tag)
                    tag_type, tag_key = tag
                    if tag_type == 'literal':
                        text += tag_key
                    elif tag_type == 'no escape':
                        text += "%s& %s %s" % (def_ldel, tag_key, def_rdel)
                    else:
                        text += "%s%s %s%s" % (def_ldel, {
                                'commment': '!',
                                'section': '#',
                                'inverted section': '^',
                                'end': '/',
                                'partial': '>',
                                'set delimiter': '=',
                                'no escape': '&',
                                'variable': ''
                            }[tag_type], tag_key, def_rdel)

                g_token_cache[text] = tags

                rend = scope(text, lambda template, data=None: render(template,
                             data={},
                             partials_path=partials_path,
                             partials_ext=partials_ext,
                             partials_dict=partials_dict,
                             padding=padding,
                             def_ldel=def_ldel, def_rdel=def_rdel,
                             scopes=data and [data]+scopes or scopes,
                             warn=warn, keep=keep))

                output += rend

            # If the scope is a sequence, an iterator or generator but not
            # derived from a string
            elif isinstance(scope, (Sequence, Iterator)) and \
                    not isinstance(scope, str):
                # Then we need to do some looping

                tags = []
                tags_with_same_key = 0
                for tag in tokens:
                    if tag == ('section', key):
                        tags_with_same_key += 1
                    if tag == ('end', key):
                        tags_with_same_key -= 1
                        if tags_with_same_key < 0:
                            break
                    tags.append(tag)

                # For every item in the scope
                for thing in scope:
                    # Append it as the most recent scope and render
                    new_scope = [thing] + scopes
                    rend = render(
                        template=tags,
                        scopes=new_scope,
                        padding=padding,
                        partials_path=partials_path,
                        partials_ext=partials_ext,
                        partials_dict=partials_dict,
                        def_ldel=def_ldel, def_rdel=def_rdel,
                        warn=warn, keep=keep)

                    output += rend
            else:
                # Otherwise, we're just a scope section
                scopes.insert(0, scope)

        # If we're an inverted section
        elif tag == 'inverted section':
            # Add the flipped scope to the scopes
            scope = _get_key(key, scopes, warn=warn, keep=keep, def_ldel=def_ldel, def_rdel=def_rdel)
            scopes.insert(0, not scope)

        # If we're a partial
        elif tag == 'partial':
            # Load the partial
            partial = _get_partial(key, partials_dict,
                                   partials_path, partials_ext)

            # Find what to pad the partial with
            left = output.rpartition('\n')[2]
            part_padding = padding
            if left.isspace():
                part_padding += left

            # Render the partial
            part_out = render(template=partial, partials_path=partials_path,
                              partials_ext=partials_ext,
                              partials_dict=partials_dict,
                              def_ldel=def_ldel, def_rdel=def_rdel,
                              padding=part_padding, scopes=scopes,
                              warn=warn, keep=keep)

            # If the partial was indented
            if left.isspace():
                # then remove the spaces from the end
                part_out = part_out.rstrip(' \t')

            # Add the partials output to the ouput
            output += part_out

    return output
