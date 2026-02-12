# Annotation Template

Use the following skeleton when annotating tensor-heavy Python code.

## File Header

```python
"""
算法摘要 (Algorithm Summary): <one-sentence purpose>

符号图例 (Symbol Legend):
- B: Batch size
- T: Sequence length
- D: Embedding dimension
- H: Number of heads
- d: Per-head dimension (D / H)

核心张量流 (Core Tensor Flow):
<input tensor> -> <projection/transform> -> <aggregation/bottleneck> -> <output tensor>
"""
```

## Function Docstring

```python
def fn(x, mask=None):
    """<中文功能说明 + English keywords>

    Args:
        x (Tensor): 输入特征。Shape: [B, T, D].
        mask (Tensor | None): 可选掩码。Shape: [1, 1, T, T] 或 [B, 1, T, T].

    Returns:
        Tensor: 输出特征。Shape: [B, T, D].

    Math & Logic:
        A = softmax((QKᵀ) / √d + M)
        Y = A V

    References:
        Ref: Eq. 1 in Vaswani et al. (2017).
    """
```

## Inline Hierarchy

```python
# ==========================================================================
# STEP 02: 多头注意力计算 (Multi-Head Attention Computation)
# ==========================================================================

# --------------------------------------------------------------------------
# step 2.1: 投影与维度重塑 (Projection & Reshaping)
# --------------------------------------------------------------------------

# step a) 线性投影
# Why: 将输入特征映射到 Q, K, V 子空间
# Shape Flow: [B, T, D] -> [B, T, 3*D]
qkv = self.qkv(x)

# step b) 维度拆解与转置
# Why: 显式分离 H 以并行计算多头注意力
# Maths: q' = q.view(B, T, H, d).transpose(1, 2)
# Shape Flow: [B, T, 3*D] -> [B, T, 3, H, d] -> [3, B, H, T, d]
q, k, v = qkv.view(B, T, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)

# --------------------------------------------------------------------------
# step 2.2: 缩放点积注意力 (Scaled Dot-Product)
# --------------------------------------------------------------------------

# step a) 相似度矩阵计算
# Why: 计算查询与键的对齐分数，并用 √d 缩放稳定梯度
# Maths: A = (Q × Kᵀ) / √d
# Shape Flow: [B, H, T, d] @ [B, H, d, T] -> [B, H, T, T]
attn = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))

# step b) 掩码应用
# Why: 屏蔽未来位置信息 (causal masking)
# Shape Flow: [B, H, T, T] + [1, 1, T, T] (Broadcast) -> [B, H, T, T]
if mask is not None:
    attn = attn + mask
```

## Constant Annotation Rule

Annotate constants inline:

- `0.1`: dropout rate, stochastic regularization to reduce overfitting.
- `1e-5`: numerical stabilizer to avoid division by zero.
- `dim=-1`: normalize across channel/feature axis.

## Output Contract

- Keep executable code logic unchanged; only annotate.
- Avoid LaTeX syntax (`$...$`, `\frac`, `\sum`); use Unicode math symbols.
- If user requests code-only output, return only the full processed Python code block.
