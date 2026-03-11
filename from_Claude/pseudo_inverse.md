好，按照 `/learn` 框架，完整讲解 Pseudoinverse（伪逆）、左伪逆和右伪逆。

---

## 阶段一：一句话定位（What & Why）

**Pseudoinverse（伪逆，也叫 Moore-Penrose 广义逆）**是当矩阵 $\mathbf{A}$ 不可逆（甚至不是方阵）时，对“逆矩阵”概念的最佳推广，用来给出线性方程组 $\mathbf{A}\mathbf{x} = \mathbf{b}$ 的“最优近似解”。

需要它的原因是：实际工程中的方程组绝大多数要么**方程比未知数多**（超定，无精确解），要么**方程比未知数少**（欠定，有无穷多解），普通逆矩阵根本不存在，必须用伪逆来处理。

---

## 阶段二：逻辑拆解（How）

### 步骤 1：为什么普通逆不够用？

一个矩阵 $\mathbf{A} \in \mathbb{C}^{m \times n}$ 只有在 $m = n$ 且满秩时才有逆矩阵 $\mathbf{A}^{-1}$，满足 $\mathbf{A}^{-1}\mathbf{A} = \mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$。

但现实中有三种常见情况，每种都需要不同处理：

| 形状 | 名称 | 问题 |
| --- | --- | --- |
| $m > n$，列满秩 | 超定（Overdetermined） | 方程比未知数多，一般无精确解 |
| $m < n$，行满秩 | 欠定（Underdetermined） | 未知数比方程多，解有无穷多个 |
| $m = n$，但秩亏 | 奇异（Singular） | 精确解不存在或不唯一 |

### 步骤 2：Moore-Penrose 伪逆的四条公理

伪逆 $\mathbf{A}^+$ 是满足以下四个 **Moore-Penrose 条件**的唯一矩阵：

$$
\text{(1) } \mathbf{A}\mathbf{A}^+\mathbf{A} = \mathbf{A}
$$

$$
\text{(2) } \mathbf{A}^+\mathbf{A}\mathbf{A}^+ = \mathbf{A}^+
$$

$$
\text{(3) } (\mathbf{A}\mathbf{A}^+)^H = \mathbf{A}\mathbf{A}^+
$$

$$
\text{(4) } (\mathbf{A}^+\mathbf{A})^H = \mathbf{A}^+\mathbf{A}
$$

条件 (1)(2) 说它是“广义逆”，条件 (3)(4) 说两个投影矩阵都是 Hermitian 的。满足这四条的 $\mathbf{A}^+$ **唯一存在**，对任意矩阵都成立。

### 步骤 3：用 SVD（奇异值分解）构造伪逆

因为任意矩阵都有 SVD（Singular Value Decomposition，奇异值分解）：

$$
\mathbf{A} = \mathbf{U}\mathbf{\Sigma}\mathbf{V}^H
$$

其中 $\mathbf{U} \in \mathbb{C}^{m\times m}$、$\mathbf{V} \in \mathbb{C}^{n\times n}$ 是酉矩阵，$\mathbf{\Sigma} \in \mathbb{R}^{m\times n}$ 是对角矩阵，对角线上是非负奇异值 $\sigma_1 \ge \sigma_2 \ge \cdots \ge 0$。

所以伪逆的通用构造公式为：

$$
\mathbf{A}^+ = \mathbf{V}\mathbf{\Sigma}^+\mathbf{U}^H
$$

其中 $\mathbf{\Sigma}^+$ 的构造规则是：把 $\mathbf{\Sigma}$ 转置，然后将每个**非零**奇异值取倒数，零奇异值保持为零。

这是最通用的伪逆，能处理任何矩阵，包括秩亏情况。

### 步骤 4：左伪逆与右伪逆（满秩的特殊情况）

当矩阵满足特定满秩条件时，伪逆可以用更简单的闭式公式表达，分两种情况：

**情况 A：列满秩（$m \ge n$，$\mathrm{rank}(\mathbf{A}) = n$）**

此时 $\mathbf{A}^H\mathbf{A} \in \mathbb{C}^{n\times n}$ 可逆，伪逆退化为**左伪逆（Left Pseudoinverse）**：

$$
\mathbf{A}^+ = \mathbf{A}^\dagger_L = (\mathbf{A}^H\mathbf{A})^{-1}\mathbf{A}^H
$$

验证：

$$
\mathbf{A}^\dagger_L \mathbf{A}
=
(\mathbf{A}^H\mathbf{A})^{-1}\mathbf{A}^H\mathbf{A}
=
\mathbf{I}_n
$$

**情况 B：行满秩（$m \le n$，$\mathrm{rank}(\mathbf{A}) = m$）**

此时 $\mathbf{A}\mathbf{A}^H \in \mathbb{C}^{m\times m}$ 可逆，伪逆退化为**右伪逆（Right Pseudoinverse）**：

$$
\mathbf{A}^+ = \mathbf{A}^\dagger_R = \mathbf{A}^H(\mathbf{A}\mathbf{A}^H)^{-1}
$$

验证：

$$
\mathbf{A}\mathbf{A}^\dagger_R
=
\mathbf{A}\mathbf{A}^H(\mathbf{A}\mathbf{A}^H)^{-1}
=
\mathbf{I}_m
$$

### 步骤 5：两种伪逆的几何意义

|  | 左伪逆 | 右伪逆 |
| --- | --- | --- |
| 适用条件 | $m > n$，列满秩（超定） | $m < n$，行满秩（欠定） |
| 满足 | $\mathbf{A}^\dagger_L \mathbf{A} = \mathbf{I}_n$ | $\mathbf{A}\mathbf{A}^\dagger_R = \mathbf{I}_m$ |
| 解的性质 | **最小二乘解**（Least Squares，残差最小） | **最小范数解**（Minimum Norm，解向量长度最小） |
| 投影含义 | $\mathbf{A}\mathbf{A}^\dagger_L$ 是向 $\mathbf{A}$ 列空间的投影 | $\mathbf{A}^\dagger_R\mathbf{A}$ 是向 $\mathbf{A}$ 行空间的投影 |

---

## 阶段三：核心例子（Example）

### Part A：日常类比

想象你是一个**侦探**，要根据目击者证词还原案发经过。

**超定（左伪逆）的场景**：10 个目击者都给你描述（方程多于未知数），但证词有出入，不可能完全自洽。左伪逆就像“综合所有证词，找一个让大家都最不满意”的折中答案，也就是最小化总误差（→ 对应步骤 4A，最小二乘解）。

**欠定（右伪逆）的场景**：只有 2 个目击者，案情有无穷多种可能吻合这 2 份证词。右伪逆就像“在所有可能的故事版本里，选最简单、最节省假设的那个”，也就是最小范数解（→ 对应步骤 4B）。

**SVD 的角色（→ 步骤 3）**：就像先把所有证词分解成几个“独立主题”，然后对每个主题单独处理，再拼回来，这样不同主题之间互不干扰。

---

### Part B：完整技术例子

我们用两个具体例子，分别演示**左伪逆（超定）**和**右伪逆（欠定）**。

---

#### 例 1：左伪逆（超定系统，最小二乘）

**问题设定**：已知线性方程组 $\mathbf{A}\mathbf{x} = \mathbf{b}$，其中

$$
\mathbf{A}
=
\begin{bmatrix}
1 & 0 \\
0 & 1 \\
1 & 1
\end{bmatrix}
\in
\mathbb{R}^{3\times 2},
\quad
\mathbf{b}
=
\begin{bmatrix}
1 \\
2 \\
4
\end{bmatrix}
$$

$m=3$ 个方程，$n=2$ 个未知数，且 $\mathrm{rank}(\mathbf{A}) = 2$（列满秩），系统超定（无精确解）。

**Step 1：计算 $\mathbf{A}^T\mathbf{A}$**（→ 步骤 4A）

$$
\mathbf{A}^T\mathbf{A}
=
\begin{bmatrix}
1 & 0 & 1 \\
0 & 1 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0 \\
0 & 1 \\
1 & 1
\end{bmatrix}
=
\begin{bmatrix}
2 & 1 \\
1 & 2
\end{bmatrix}
$$

**Step 2：求 $(\mathbf{A}^T\mathbf{A})^{-1}$**

$$
\det
\begin{bmatrix}
2 & 1 \\
1 & 2
\end{bmatrix}
=
4-1
=
3
$$

$$
(\mathbf{A}^T\mathbf{A})^{-1}
=
\frac{1}{3}
\begin{bmatrix}
2 & -1 \\
-1 & 2
\end{bmatrix}
$$

**Step 3：构造左伪逆 $\mathbf{A}^\dagger_L = (\mathbf{A}^T\mathbf{A})^{-1}\mathbf{A}^T$**

$$
\mathbf{A}^\dagger_L
=
\frac{1}{3}
\begin{bmatrix}
2 & -1 \\
-1 & 2
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 1 \\
0 & 1 & 1
\end{bmatrix}
=
\frac{1}{3}
\begin{bmatrix}
2 & -1 & 1 \\
-1 & 2 & 1
\end{bmatrix}
$$

验证 $\mathbf{A}^\dagger_L \mathbf{A} = \mathbf{I}_2$：

$$
\frac{1}{3}
\begin{bmatrix}
2 & -1 & 1 \\
-1 & 2 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0 \\
0 & 1 \\
1 & 1
\end{bmatrix}
=
\frac{1}{3}
\begin{bmatrix}
3 & 0 \\
0 & 3
\end{bmatrix}
=
\mathbf{I}_2
\checkmark
$$

**Step 4：求最小二乘解**

$$
\hat{\mathbf{x}}
=
\mathbf{A}^\dagger_L \mathbf{b}
=
\frac{1}{3}
\begin{bmatrix}
2 & -1 & 1 \\
-1 & 2 & 1
\end{bmatrix}
\begin{bmatrix}
1 \\
2 \\
4
\end{bmatrix}
=
\frac{1}{3}
\begin{bmatrix}
4 \\
7
\end{bmatrix}
=
\begin{bmatrix}
4/3 \\
7/3
\end{bmatrix}
$$

**Step 5：验证残差最小**

$$
\mathbf{A}\hat{\mathbf{x}}
=
\begin{bmatrix}
1 & 0 \\
0 & 1 \\
1 & 1
\end{bmatrix}
\begin{bmatrix}
4/3 \\
7/3
\end{bmatrix}
=
\begin{bmatrix}
4/3 \\
7/3 \\
11/3
\end{bmatrix}
$$

残差向量 $\mathbf{r} = \mathbf{b} - \mathbf{A}\hat{\mathbf{x}}$：

$$
\mathbf{r}
=
\begin{bmatrix}
1 \\
2 \\
4
\end{bmatrix}
-
\begin{bmatrix}
4/3 \\
7/3 \\
11/3
\end{bmatrix}
=
\begin{bmatrix}
-1/3 \\
-1/3 \\
1/3
\end{bmatrix}
$$

$$
\|\mathbf{r}\|^2
=
\frac{1}{9}+\frac{1}{9}+\frac{1}{9}
=
\frac{1}{3}
$$

这是所有可能 $\mathbf{x}$ 中残差平方和最小的解（Normal Equation 的解）。三个方程无法同时满足，但误差被均摊到最小。

---

#### 例 2：右伪逆（欠定系统，最小范数）

**问题设定**：

$$
\mathbf{A}
=
\begin{bmatrix}
1 & 2 & 0 \\
0 & 1 & 1
\end{bmatrix}
\in
\mathbb{R}^{2\times 3},
\quad
\mathbf{b}
=
\begin{bmatrix}
3 \\
2
\end{bmatrix}
$$

$m=2$ 个方程，$n=3$ 个未知数，$\mathrm{rank}(\mathbf{A}) = 2$（行满秩），系统欠定（有无穷多解）。

**Step 1：计算 $\mathbf{A}\mathbf{A}^T$**（→ 步骤 4B）

$$
\mathbf{A}\mathbf{A}^T
=
\begin{bmatrix}
1 & 2 & 0 \\
0 & 1 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0 \\
2 & 1 \\
0 & 1
\end{bmatrix}
=
\begin{bmatrix}
5 & 2 \\
2 & 2
\end{bmatrix}
$$

**Step 2：求 $(\mathbf{A}\mathbf{A}^T)^{-1}$**

$$
\det
\begin{bmatrix}
5 & 2 \\
2 & 2
\end{bmatrix}
=
10-4
=
6
$$

$$
(\mathbf{A}\mathbf{A}^T)^{-1}
=
\frac{1}{6}
\begin{bmatrix}
2 & -2 \\
-2 & 5
\end{bmatrix}
$$

**Step 3：构造右伪逆 $\mathbf{A}^\dagger_R = \mathbf{A}^T(\mathbf{A}\mathbf{A}^T)^{-1}$**

$$
\mathbf{A}^\dagger_R
=
\begin{bmatrix}
1 & 0 \\
2 & 1 \\
0 & 1
\end{bmatrix}
\frac{1}{6}
\begin{bmatrix}
2 & -2 \\
-2 & 5
\end{bmatrix}
=
\frac{1}{6}
\begin{bmatrix}
2 & -2 \\
2 & 1 \\
-2 & 5
\end{bmatrix}
$$

验证 $\mathbf{A}\mathbf{A}^\dagger_R = \mathbf{I}_2$：

$$
\frac{1}{6}
\begin{bmatrix}
1 & 2 & 0 \\
0 & 1 & 1
\end{bmatrix}
\begin{bmatrix}
2 & -2 \\
2 & 1 \\
-2 & 5
\end{bmatrix}
=
\frac{1}{6}
\begin{bmatrix}
6 & 0 \\
0 & 6
\end{bmatrix}
=
\mathbf{I}_2
\checkmark
$$

**Step 4：求最小范数解**

$$
\hat{\mathbf{x}}
=
\mathbf{A}^\dagger_R \mathbf{b}
=
\frac{1}{6}
\begin{bmatrix}
2 & -2 \\
2 & 1 \\
-2 & 5
\end{bmatrix}
\begin{bmatrix}
3 \\
2
\end{bmatrix}
=
\frac{1}{6}
\begin{bmatrix}
2 \\
8 \\
4
\end{bmatrix}
=
\begin{bmatrix}
1/3 \\
4/3 \\
2/3
\end{bmatrix}
$$

**Step 5：验证是精确解且范数最小**

$$
\mathbf{A}\hat{\mathbf{x}}
=
\begin{bmatrix}
1 & 2 & 0 \\
0 & 1 & 1
\end{bmatrix}
\begin{bmatrix}
1/3 \\
4/3 \\
2/3
\end{bmatrix}
=
\begin{bmatrix}
3 \\
2
\end{bmatrix}
=
\mathbf{b}
\checkmark
$$

$$
\|\hat{\mathbf{x}}\|^2
=
\frac{1}{9}+\frac{16}{9}+\frac{4}{9}
=
\frac{21}{9}
=
\frac{7}{3}
\approx
2.33
$$

这是所有满足 $\mathbf{A}\mathbf{x}=\mathbf{b}$ 的解中，$\|\mathbf{x}\|^2$ 最小的一个（可以验证，其他解的范数都更大）。

---

## 阶段四：图解辅助（Visual Aid）🖼️

> A clean educational diagram on white background comparing three scenarios: square invertible matrix, overdetermined system (left pseudoinverse), and underdetermined system (right pseudoinverse).
>
> Layout: Three columns, each with a top block showing matrix shape, a middle block showing the key equation, and a bottom block showing the geometric interpretation.
>
> Left column titled "Square Invertible (m=n, full rank)": Matrix icon labeled "A in R^(n x n)" drawn as a square. Equation: "A^{-1}A = AA^{-1} = I". Geometry: A single vector b with a unique arrow pointing to x = A^{-1}b. Label: "Unique exact solution".
>
> Middle column titled "Overdetermined / Left Pseudoinverse (m > n)": Matrix icon drawn as a tall rectangle, labeled "A in R^(m x n), m > n". Equation: "A^dagger_L = (A^T A)^{-1}A^T, A^dagger_L A = I". Geometry: Show a 2D plane (column space of A) in a 3D space. Point b is above the plane (not reachable). A dashed perpendicular line drops from b to the closest point Ax-hat on the plane. Arrow from b to Ax-hat labeled "residual r = b - Ax-hat (minimized)". Label: "Least squares solution: minimize ||b - Ax||^2".
>
> Right column titled "Underdetermined / Right Pseudoinverse (m < n)": Matrix icon drawn as a wide rectangle, labeled "A in R^(m x n), m < n". Equation: "A^dagger_R = A^T(AA^T)^{-1}, AA^dagger_R = I". Geometry: Show a 1D line (solution set, an affine subspace) in a 2D space. Multiple dots on the line, all satisfying Ax = b. One dot at the closest point to the origin, labeled "x-hat = minimum norm solution". Dashed line from origin to x-hat. Label: "Minimum norm solution: minimize ||x||^2".
>
> Key elements: (1) matrix shape icons (square / tall / wide), (2) which identity each pseudoinverse satisfies, (3) residual minimization geometry for left, (4) minimum norm geometry for right, (5) color coding: blue for left pseudoinverse, green for right pseudoinverse, gray for square case.
>
> Style: minimalist technical illustration, labeled with clear bold English text. Clean lines, high contrast, white background. No decorative elements.

📌 **图解说明**：

- 左列（方阵）：经典可逆情况，作为对比基准。对应步骤 1。
- 中列（左伪逆）：$\mathbf{b}$ 不在 $\mathbf{A}$ 的列空间内，最小二乘解是列空间上距 $\mathbf{b}$ 最近的点。对应步骤 4A。
- 右列（右伪逆）：解空间是一条直线（仿射子空间），最小范数解是该直线上距原点最近的点。对应步骤 4B。

---

## 阶段五：边界与延伸（Boundary）

### 适用边界

左伪逆 $(\mathbf{A}^H\mathbf{A})^{-1}\mathbf{A}^H$ 要求 $\mathbf{A}^H\mathbf{A}$ 可逆，即**严格列满秩**。如果矩阵有重复列或存在多重共线性（Collinearity），$\mathbf{A}^H\mathbf{A}$ 会接近奇异，数值上极不稳定，必须改用 SVD 截断版伪逆（Truncated SVD），或者加正则化（Tikhonov Regularization，即 Ridge Regression）：

$$
\hat{\mathbf{x}}
=
(\mathbf{A}^H\mathbf{A} + \lambda\mathbf{I})^{-1}\mathbf{A}^H \mathbf{b}
$$

### 常见误解

1. **“伪逆就是最小二乘”**：不完全对。左伪逆给出最小二乘解（超定时），右伪逆给出最小范数解（欠定时），只有在列满秩超定情况下，“伪逆解”才等于“最小二乘解”。
2. **“$\mathbf{A}^+\mathbf{A} = \mathbf{I}$”**：这只对列满秩时成立（左伪逆）。一般情况下，$\mathbf{A}^+\mathbf{A}$ 只是一个投影矩阵，满足 $(\mathbf{A}^+\mathbf{A})^2 = \mathbf{A}^+\mathbf{A}$，并不等于单位矩阵。

### 延伸方向

- **SVD 的全貌**：伪逆最通用的构造方式，也是数值计算中实际使用的方法（`numpy.linalg.pinv` 内部就是 SVD）。
- **正则化（Regularization）**：当矩阵接近奇异时的伪逆替代方案，直接连接到 Tikhonov 正则化和贝叶斯估计。
- **在 DOA 估计和波束成形中**：协方差矩阵求逆（MVDR 中的 $\mathbf{R}^{-1}$）在快拍数不足时矩阵秩亏，此时用伪逆或加对角载入（Diagonal Loading）是标准做法。
