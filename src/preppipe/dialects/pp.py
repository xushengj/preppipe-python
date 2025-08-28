# SPDX-FileCopyrightText: 2025 PrepPipe's Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import xdsl.ir
import xdsl.irdl
import xdsl.dialects.builtin

# ==============================================================
# Traits
# ==============================================================

class PPMetadataTrait(xdsl.irdl.OpTrait):
  '''This trait indicates that the operation is only carrying metadata that does not affect program semantics.

  During conversion and transforms, operations with this trait should be directly copied to the output without any modification.
  '''

class PPAssetDeclarationTrait(xdsl.irdl.OpTrait):
  pass

# ==============================================================
# Attributes
# ==============================================================

class PPImageLikeType(xdsl.ir.Attribute):
  pass

class PPAudioLikeType(xdsl.ir.Attribute):
  pass

_pp_attributes = [
  PPImageLikeType,
  PPAudioLikeType,
]

# ==============================================================
# Types
# ==============================================================

@xdsl.irdl.irdl_attr_definition
class PPImageType(xdsl.ir.TypeAttribute, PPImageLikeType):
  name = "pp.image"

@xdsl.irdl.irdl_attr_definition
class PPAudioType(xdsl.ir.TypeAttribute, PPAudioLikeType):
  name = "pp.audio"

# ==============================================================
# Ops
# ==============================================================

@xdsl.irdl.irdl_op_definition
class PPCommentOp(xdsl.irdl.IRDLOperation):
  name = "pp.comment"
  comment = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  assembly_format = "attr-dict $comment"
  traits = xdsl.irdl.traits_def(PPMetadataTrait())

  def __init__(self, comment : str | xdsl.dialects.builtin.StringAttr) -> None:
    comment_attr = xdsl.dialects.builtin.StringAttr(comment) if isinstance(comment, str) else comment
    super().__init__(properties={"comment": comment_attr})

@xdsl.irdl.irdl_op_definition
class PPErrorOp(xdsl.irdl.IRDLOperation):
  name = "pp.error"
  code = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  message = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  assembly_format = "attr-dict $code, $message"
  traits = xdsl.irdl.traits_def(PPMetadataTrait())

  def __init__(self, code : str | xdsl.dialects.builtin.StringAttr, message : str | xdsl.dialects.builtin.StringAttr) -> None:
    code_attr = xdsl.dialects.builtin.StringAttr(code) if isinstance(code, str) else code
    message_attr = xdsl.dialects.builtin.StringAttr(message) if isinstance(message, str) else message
    super().__init__(properties={"code": code_attr, "message": message_attr})

@xdsl.irdl.irdl_op_definition
class PPImageDeclOp(xdsl.irdl.IRDLOperation):
  name = "pp.image_decl"
  file_path = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  outputs = xdsl.irdl.result_def(PPImageType)
  assembly_format = "attr-dict $file_path"
  traits = xdsl.irdl.traits_def(PPAssetDeclarationTrait())

  def __init__(self,
               file_path : str | xdsl.dialects.builtin.StringAttr) -> None:
    file_path_attr = xdsl.dialects.builtin.StringAttr(file_path) if isinstance(file_path, str) else file_path
    super().__init__(properties={"file_path": file_path_attr})

@xdsl.irdl.irdl_op_definition
class PPAudioDeclOp(xdsl.irdl.IRDLOperation):
  name = "pp.audio_decl"
  file_path = xdsl.irdl.prop_def(xdsl.dialects.builtin.StringAttr)
  outputs = xdsl.irdl.result_def(PPAudioType)
  assembly_format = "attr-dict $file_path"
  traits = xdsl.irdl.traits_def(PPAssetDeclarationTrait())

  def __init__(self,
               file_path : str | xdsl.dialects.builtin.StringAttr) -> None:
    file_path_attr = xdsl.dialects.builtin.StringAttr(file_path) if isinstance(file_path, str) else file_path
    super().__init__(properties={"file_path": file_path_attr})

_pp_operations = [
  PPCommentOp,
  PPErrorOp,
  PPImageDeclOp,
  PPAudioDeclOp,
]

# ==============================================================
# Dialect
# ==============================================================

PP = xdsl.ir.Dialect("pp", _pp_operations, _pp_attributes)
