# SPDX-FileCopyrightText: 2025 PrepPipe's Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import chardet
import xdsl
import xdsl.ir
import xdsl.dialects.builtin
import typing

from ...dialects.pp import *
from ...dialects.im import *
from ...pipeline import *

def _parsetext(ctx : ContextWrapper, path : str) -> xdsl.ir.Operation:
  with open(path, "rb") as f:
    data = f.read()
    det = chardet.detect(data, should_rename_legacy=True)
    strcontent = data.decode(encoding=det["encoding"], errors="ignore")
    #difile = ctx.get_DIFile(path)
    name = os.path.splitext(os.path.basename(path))[0]
    nameattr = ctx.get_xdsl_stringattr(name)
    doc = IMDocumentOp(filename=nameattr)
    lines = strcontent.splitlines(keepends=False)
    row = 0
    for line in lines:
      row += 1
      block = xdsl.ir.Block()
      doc.body.add_block(block)
      if len(line) > 0:
        #loc = ctx.get_DILocation(difile, 0, row, 1)
        e = IMTextOp(line)

        e = IMElementOp.create(StringLiteral.get(line, ctx), '', loc)
        block.push_back(e)
    return doc

@FrontendDecl('in', input_decl=IODecl('Story Script Files', match_suffix=('docx', 'odt', 'md', 'txt'), nargs='+'), output_decl=xdsl.ir.Operation)
class InputHandler(TransformBase):
  def _dispatch_read(self, path : str) -> xdsl.ir.Operation:
    if not isinstance(path, str):
      raise PPInternalError("InputHandler only accepts file path strings as input")
    base, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext == '.txt':
      return _parsetext(self._ctx, path)
    raise PPInternalError(f"Unsupported input file type: {ext}")

  def run(self) -> xdsl.ir.Operation | typing.List[xdsl.ir.Operation]:
    results = []
    for f in self.inputs:
      if not isinstance(f, str):
        raise PPInternalError("InputHandler only accepts file path strings as input")
      results.append(self._dispatch_read(f))
    module = xdsl.dialects.builtin.ModuleOp()
    for r in results:
      module.body.add_op(r)
    return module
