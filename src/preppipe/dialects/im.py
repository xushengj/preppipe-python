# SPDX-FileCopyrightText: 2025 PrepPipe's Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing
import xdsl.ir
import xdsl.irdl
import xdsl.dialects.builtin

from .pp import *

# ==============================================================
# Ops
# ==============================================================

@xdsl.irdl.irdl_op_definition
class IMTextOp(xdsl.irdl.IRDLOperation):
  name = "im.text"
  content = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  assembly_format = "attr-dict $content"

  def __init__(self, content : str | xdsl.dialects.builtin.StringAttr) -> None:
    content_attr = xdsl.dialects.builtin.StringAttr(content) if isinstance(content, str) else content
    super().__init__(properties={"content": content_attr})

@xdsl.irdl.irdl_op_definition
class IMSpecialBlockOp(xdsl.irdl.IRDLOperation):
  name = "im.special_block"
  content = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr) # '\n' 分割的多行文本
  reason = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  assembly_format = "attr-dict [$reason] $content"

  ATTR_REASON_BG_HIGHLIGHT : typing.ClassVar[str] = 'bg_highlight' # 这段文本有段落背景色
  ATTR_REASON_CENTERED : typing.ClassVar[str] = 'centered' # 这段文本不是“正文”而是各种标题

  def __init__(self, content : str | xdsl.dialects.builtin.StringAttr, reason : str | xdsl.dialects.builtin.StringAttr) -> None:
    content_attr = xdsl.dialects.builtin.StringAttr(content) if isinstance(content, str) else content
    reason_attr = xdsl.dialects.builtin.StringAttr(reason) if isinstance(reason, str) else reason
    assert reason_attr.value in [
      IMSpecialBlockOp.ATTR_REASON_BG_HIGHLIGHT,
      IMSpecialBlockOp.ATTR_REASON_CENTERED,
    ]
    super().__init__(properties={"content": content_attr, "reason": reason_attr})

@xdsl.irdl.irdl_op_definition
class IMListOp(xdsl.irdl.IRDLOperation):
  name = "im.list"

  def get_num_items(self) -> int:
    return len(self.regions)

  def add_list_item(self) -> xdsl.ir.Region:
    new_region = xdsl.ir.Region()
    self.add_region(new_region)
    return new_region

  def get_list_item(self, index : int) -> xdsl.ir.Region:
    return self.regions[index]

  def take_list_item(self, list_item : int | xdsl.ir.Region) -> None:
    self.detach_region(list_item)

@xdsl.irdl.irdl_op_definition
class IMTableCellOp(xdsl.irdl.IRDLOperation):
  name = "im.table_cell"
  row = xdsl.irdl.prop_def(xdsl.dialects.builtin.IntegerAttr)
  col = xdsl.irdl.prop_def(xdsl.dialects.builtin.IntegerAttr)
  body = xdsl.irdl.region_def("single_block")
  assembly_format = "attr-dict [$row, $col]"

  def __init__(self, row : int | xdsl.dialects.builtin.IntegerAttr, col : int | xdsl.dialects.builtin.IntegerAttr) -> None:
    row_attr = xdsl.dialects.builtin.IntegerAttr(row, value_type=xdsl.dialects.builtin.IndexType()) if isinstance(row, int) else row
    col_attr = xdsl.dialects.builtin.IntegerAttr(col, value_type=xdsl.dialects.builtin.IndexType()) if isinstance(col, int) else col
    super().__init__(properties={"row": row_attr, "col": col_attr})

@xdsl.irdl.irdl_op_definition
class IMTableOp(xdsl.irdl.IRDLOperation):
  name = "im.table"
  body = xdsl.irdl.region_def("single_block")

@xdsl.irdl.irdl_op_definition
class IMAssetOp(xdsl.irdl.IRDLOperation):
  _T = xdsl.irdl.VarConstraint("T", xdsl.irdl.AnyAttr())
  name = "im.asset"
  value = xdsl.irdl.operand_def(_T)
  assembly_format = "attr-dict $value"

  def __init__(self, value : xdsl.irdl.TypedAttribute) -> None:
    super().__init__(operands=[value], properties={})
