# SPDX-FileCopyrightText: 2025 PrepPipe's Contributors
# SPDX-License-Identifier: Apache-2.0

from preppipe.util.audit import FileAccessAuditor
from ..irbase import *
import xdsl
import xdsl.ir
import xdsl.context
import xdsl.dialects.builtin

class ContextWrapper(Context):
  # 该类有以下两个目标：
  # 1. 用于将 irbase.Context 和 xdsl.context.Context 并在一起，用于在过渡时期替代 irbase.Context
  # 2. xDSL 不使用 Context 来给对象去重（包括类型、属性等），这里我们自己搞一个去重机制来节省内存、提高效率
  _xdsl_ctx : xdsl.context.Context
  _xdsl_unknownloc : xdsl.dialects.builtin.UnknownLoc
  _xdsl_stringattr_cache : dict[str, xdsl.dialects.builtin.StringAttr]
  _xdsl_intattr_cache : dict[int, xdsl.dialects.builtin.IntAttr[int]]
  _xdsl_filelineloc_cache : dict[tuple[xdsl.dialects.builtin.StringAttr, xdsl.dialects.builtin.IntAttr[int], xdsl.dialects.builtin.IntAttr[int]], xdsl.dialects.builtin.FileLineColLoc]

  def __init__(self, file_auditor: FileAccessAuditor | None = None) -> None:
    super().__init__(file_auditor)
    self._xdsl_ctx = xdsl.context.Context()
    self._xdsl_unknownloc = xdsl.dialects.builtin.UnknownLoc()
    self._xdsl_stringattr_cache = {}
    self._xdsl_intattr_cache = {}
    self._xdsl_filelineloc_cache = {}

  def get_xdsl_context(self) -> xdsl.context.Context:
    return self._xdsl_ctx

  def get_xdsl_stringattr(self, value : str) -> xdsl.dialects.builtin.StringAttr:
    if value not in self._xdsl_stringattr_cache:
      str_attr = xdsl.dialects.builtin.StringAttr(value)
      self._xdsl_stringattr_cache[value] = str_attr
    return self._xdsl_stringattr_cache[value]

  def get_xdsl_intattr(self, value : int) -> xdsl.dialects.builtin.IntAttr[int]:
    if value not in self._xdsl_intattr_cache:
      int_attr = xdsl.dialects.builtin.IntAttr(value)
      self._xdsl_intattr_cache[value] = int_attr
    return self._xdsl_intattr_cache[value]

  def get_xdsl_unknownloc(self) -> xdsl.dialects.builtin.UnknownLoc:
    return self._xdsl_unknownloc

  def get_xdsl_filelineloc(self, filename : xdsl.dialects.builtin.StringAttr, line : xdsl.dialects.builtin.IntAttr[int], column : xdsl.dialects.builtin.IntAttr[int]) -> xdsl.dialects.builtin.FileLineColLoc:
    key = (filename, line, column)
    if key not in self._xdsl_filelineloc_cache:
      loc_attr = xdsl.dialects.builtin.FileLineColLoc(filename, line, column)
      self._xdsl_filelineloc_cache[key] = loc_attr
    return self._xdsl_filelineloc_cache[key]