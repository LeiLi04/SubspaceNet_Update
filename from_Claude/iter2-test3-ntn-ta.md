## 阶段一：一句话定位（What & Why）

NTN（Non-Terrestrial Network，非地面网络）中的 Timing Advance（TA，定时提前）补偿是指终端根据到卫星的传播时延，提前发送上行信号，使信号恰好在基站/卫星预期的时间窗口内到达。需要它的原因是：NTN 中卫星距地面数百到数万公里，单程传播时延可达数毫秒到上百毫秒（LEO 约 2-7 ms，GEO 约 120 ms），如果不补偿，终端发出的上行信号到达卫星时将严重偏离其分配的时隙，与其他用户的信号发生碰撞，整个上行接入机制将完全崩溃。

## 阶段二：逻辑拆解（How）

核心逻辑链条：

1. **地面网络的假设被打破**：在传统地面蜂窝网络中，基站到终端的距离通常在几百米到几公里，往返时延（RTT）在微秒量级。3GPP 的上行定时机制（基于 TA 命令的闭环调整）是为这个量级设计的。因为 NTN 的传播距离增加了 3-5 个数量级（LEO ~600 km，GEO ~35,786 km），RTT 从微秒级跳到毫秒甚至百毫秒级，远超地面系统 TA 命令的调整范围。

2. **差分时延问题**：更棘手的是，同一波束覆盖范围内的不同终端到卫星的距离不同。对于 LEO 卫星，波束覆盖直径可达数百公里，波束边缘和中心的终端到卫星的路径差可导致数毫秒的差分时延（differential delay）。如果不补偿这个差分，不同终端的上行信号到达卫星的时间错开，无法对齐到同一个上行时隙。

3. **两级补偿架构**：因为总时延太大且终端间差异显著，所以 3GPP 在 NTN 中设计了两级 TA 补偿机制：
   - **公共 TA（Common TA）**：由网络广播，补偿波束中心点到卫星的参考时延。所有终端共享这个值。它解决了"量级"问题。
   - **终端自主 TA（UE-specific TA）**：每个终端根据自身 GNSS 位置和星历数据，自主计算自己到卫星的距离与参考点的差值，进一步补偿差分时延。这解决了"差异"问题。

4. **动态更新的必要性**：关键在于，卫星在持续运动（LEO 卫星速度约 7.5 km/s），因此终端到卫星的距离每时每刻都在变化。公共 TA 需要随卫星位置持续更新（通过系统信息广播），终端自主 TA 也需要实时根据星历数据重新计算。NTN 中的 TA 不是一次性校准，而是一个持续跟踪的动态过程。

5. **对上行同步精度的要求**：最终目标是让所有终端的上行信号到达卫星时的定时误差控制在 CP（Cyclic Prefix）长度以内。在 5G NR 中，以 SCS=15 kHz 为例，CP 长度约为 4.7 μs。这意味着所有终端的残余定时误差必须小于这个值，否则会破坏上行 OFDM 信号的正交性，导致用户间干扰。

## 阶段三：核心例子（Example）

### Part A: 日常类比

想象一个交响乐团在排练，但指挥（卫星）站在 1 公里以外的山顶上。

- 在普通音乐厅里（地面网络），指挥就在眼前，所有乐手看到指挥棒落下就演奏，同步毫无问题。（→ 对应步骤 1 的假设）
- 现在指挥站在 1 公里外。声音传播需要约 3 秒，如果乐手"听到"指挥的拍子再演奏，等声音传回去时已经晚了 3 秒。所以每个乐手必须"提前 3 秒"开始演奏。（→ 对应步骤 1 的大时延问题）
- 但问题是，乐手们分布在一片空地上，有的离指挥 900 米，有的离 1100 米。如果所有人都提前同样的 3 秒，近处的声音会早到，远处的会晚到。所以每个乐手需要根据自己到指挥的精确距离，各自微调提前量。（→ 对应步骤 2、3 的两级补偿）
- 更复杂的是，指挥站在一辆缓缓移动的卡车上（卫星在运动），所以每个乐手还需要持续重新计算距离并调整提前量。（→ 对应步骤 4）
- 最终要求是：所有乐手的声音到达指挥耳朵的时刻误差不能超过 0.01 秒，否则和声就乱了。（→ 对应步骤 5）

### Part B: 完整技术例子

**问题设定**：

一个 LEO NTN 系统的具体 TA 计算。

- 卫星轨道高度：$h = 600\text{ km}$
- 卫星星下点（nadir）坐标：设为原点 O
- 卫星位置（笛卡尔坐标，以地心为参考）：直接简化为地面投影问题，卫星在地面上方 $h = 600\text{ km}$
- 波束覆盖：圆形波束，地面覆盖直径 $D = 100\text{ km}$（半径 50 km）
- 波束参考点：波束中心，即星下点 O
- 终端 A（UE_A）：位于波束中心 O
- 终端 B（UE_B）：位于波束边缘，距中心 50 km
- 终端 C（UE_C）：位于波束中间，距中心 25 km
- 5G NR 参数：SCS = 15 kHz，CP 长度 $T_{CP} = 4.69\ \mu s$
- 光速：$c = 3 \times 10^5\text{ km/s}$
- 卫星运动速度：$v_{sat} = 7.56\text{ km/s}$（600 km LEO 轨道的典型值）

---

**Step 1: 计算各终端到卫星的斜距（slant range）**（→ 对应步骤 1、2）

假设地球表面局部平坦（对 100 km 尺度的近似误差 < 0.1%），卫星位于终端正上方 $h = 600\text{ km}$ 处。

终端到卫星的斜距用勾股定理：

$$d = \sqrt{h^2 + r^2}$$

其中 $r$ 是终端到星下点的水平距离。

**UE_A**（$r_A = 0$）：

$$d_A = \sqrt{600^2 + 0^2} = 600.000\text{ km}$$

**UE_B**（$r_B = 50\text{ km}$）：

$$d_B = \sqrt{600^2 + 50^2} = \sqrt{360000 + 2500} = \sqrt{362500} = 602.080\text{ km}$$

**UE_C**（$r_C = 25\text{ km}$）：

$$d_C = \sqrt{600^2 + 25^2} = \sqrt{360000 + 625} = \sqrt{360625} = 600.521\text{ km}$$

---

**Step 2: 计算单程传播时延**（→ 对应步骤 1）

$$\tau = \frac{d}{c}$$

**UE_A**：

$$\tau_A = \frac{600.000}{3 \times 10^5} = 2.000000\text{ ms}$$

**UE_B**：

$$\tau_B = \frac{602.080}{3 \times 10^5} = 2.006933\text{ ms}$$

**UE_C**：

$$\tau_C = \frac{600.521}{3 \times 10^5} = 2.001737\text{ ms}$$

---

**Step 3: 计算往返时延（RTT）和差分时延**（→ 对应步骤 2）

往返时延 $\text{RTT} = 2\tau$：

| 终端 | 斜距 (km) | 单程时延 (ms) | RTT (ms) |
|------|----------|---------------|----------|
| UE_A | 600.000 | 2.000000 | 4.000000 |
| UE_B | 602.080 | 2.006933 | 4.013867 |
| UE_C | 600.521 | 2.001737 | 4.003473 |

以波束中心 UE_A 为参考，差分 RTT：

$$\Delta\text{RTT}_B = \text{RTT}_B - \text{RTT}_A = 4.013867 - 4.000000 = 13.867\ \mu s$$

$$\Delta\text{RTT}_C = \text{RTT}_C - \text{RTT}_A = 4.003473 - 4.000000 = 3.473\ \mu s$$

**关键对比**：CP 长度为 $T_{CP} = 4.69\ \mu s$

- UE_B 的差分 RTT = $13.867\ \mu s$，是 CP 长度的 **2.96 倍** → 如果不做终端自主 TA，严重超出容忍范围
- UE_C 的差分 RTT = $3.473\ \mu s$，小于 CP → 勉强可以容忍，但余量很小

---

**Step 4: 两级 TA 补偿计算**（→ 对应步骤 3）

**第一级：公共 TA（Common TA）**

网络广播波束中心的参考 RTT 作为公共 TA 值：

$$\text{TA}_{common} = \text{RTT}_{ref} = \text{RTT}_A = 4.000000\text{ ms}$$

所有终端收到此值后，将上行发送时间提前 $\text{TA}_{common}$。

应用公共 TA 后的残余时延：

| 终端 | 原始 RTT (ms) | 公共 TA (ms) | 残余 (μs) |
|------|-------------|-------------|----------|
| UE_A | 4.000000 | 4.000000 | **0** |
| UE_B | 4.013867 | 4.000000 | **13.867** |
| UE_C | 4.003473 | 4.000000 | **3.473** |

UE_A 完美对齐。UE_B 残余 13.867 μs 仍远超 CP。

**第二级：终端自主 TA（UE-specific TA）**

每个终端利用 GNSS 获取自身位置，结合网络广播的卫星星历数据，自主计算：

$$\text{TA}_{UE} = \frac{2(d_{UE} - d_{ref})}{c}$$

**UE_B**：

$$\text{TA}_{UE\_B} = \frac{2(602.080 - 600.000)}{3 \times 10^5} = \frac{2 \times 2.080}{300000} = 13.867\ \mu s$$

**UE_C**：

$$\text{TA}_{UE\_C} = \frac{2(600.521 - 600.000)}{3 \times 10^5} = \frac{2 \times 0.521}{300000} = 3.473\ \mu s$$

应用两级 TA 后：

| 终端 | 残余 after 公共 TA (μs) | 终端自主 TA (μs) | 最终残余 (μs) |
|------|------------------------|-----------------|--------------|
| UE_A | 0 | 0 | **0** |
| UE_B | 13.867 | 13.867 | **≈ 0** |
| UE_C | 3.473 | 3.473 | **≈ 0** |

在理想 GNSS 定位精度下，所有终端的残余定时误差趋近于零，远小于 CP = 4.69 μs。

---

**Step 5: 考虑卫星运动的动态 TA 更新**（→ 对应步骤 4）

LEO 卫星以 $v_{sat} = 7.56\text{ km/s}$ 运动。考虑最坏情况：卫星沿径向（远离/接近终端的方向）运动。

时延变化率（delay rate）：

$$\dot{\tau} = \frac{v_{radial}}{c}$$

对于径向速度的上界估计，考虑卫星从仰角 90°（正上方）运动到仰角 10°（接近地平线）。在仰角 $\theta_{el}$ 处，径向速度分量为：

$$v_{radial} = v_{sat} \cos(\theta_{el})$$

最坏情况（低仰角 $\theta_{el} = 10°$）：

$$v_{radial,max} \approx 7.56 \times \cos(10°) = 7.56 \times 0.985 = 7.44\text{ km/s}$$

对应的单程时延变化率：

$$\dot{\tau}_{max} = \frac{7.44}{3 \times 10^5} = 24.8\ \mu s/s$$

RTT 变化率（双程）：

$$\dot{\text{RTT}}_{max} = 2\dot{\tau}_{max} = 49.6\ \mu s/s$$

这意味着：如果 TA 不更新，每秒钟累积的定时误差约为 49.6 μs。

要保证残余误差 < CP/2 ≈ 2.35 μs，TA 的最大更新间隔为：

$$T_{update,max} = \frac{T_{CP}/2}{\dot{\text{RTT}}_{max}} = \frac{2.35}{49.6} \approx 47.4\text{ ms}$$

即大约每 50 ms 需要更新一次 TA。在 3GPP NTN 规范中，公共 TA 通过 SIB19 广播更新，终端自主 TA 则根据星历数据持续自主计算（更新频率通常远高于 50 ms）。

---

**Step 6: GNSS 定位误差的影响**（→ 对应步骤 5 的精度要求）

实际中 GNSS 定位存在误差。假设终端位置误差为 $\Delta r$（水平），对应的斜距误差为：

$$\Delta d \approx \frac{r \cdot \Delta r}{\sqrt{h^2 + r^2}}$$

对于 UE_B（$r = 50\text{ km}$）：

$$\Delta d \approx \frac{50 \cdot \Delta r}{602.08} \approx 0.083 \cdot \Delta r$$

双程定时误差：

$$\Delta\text{RTT} = \frac{2\Delta d}{c} = \frac{2 \times 0.083 \cdot \Delta r}{3 \times 10^5}$$

要求 $\Delta\text{RTT} < T_{CP} = 4.69\ \mu s$：

$$\Delta r < \frac{4.69 \times 10^{-6} \times 3 \times 10^5}{2 \times 0.083} = \frac{1.407}{0.166} \approx 8.47\text{ km}$$

所以 GNSS 定位精度在公里量级（通常 < 10 m）完全满足要求，余量充足。但如果是在 GNSS 不可用的降级场景下，定位精度可能退化到公里级，此时需要网络辅助的 TA 补偿机制。

---

**结论总结**：

通过这个具体数值例子，我们看到：
1. 公共 TA 解决了约 4 ms 的大时延偏移（对应 600 km 的传播距离）
2. 终端自主 TA 解决了高达 13.867 μs 的差分时延（对应波束边缘 50 km 的路径差），这一值是 CP 的 2.96 倍，不补偿则上行通信完全失败
3. 卫星运动要求每约 50 ms 更新 TA，否则累积误差会超过 CP
4. GNSS 定位精度对 TA 补偿来说余量充足（要求 < 8.47 km，实际精度 < 10 m）

## 阶段四：图解辅助（Visual Aid）🖼️

> A clean educational diagram on white background showing NTN timing advance compensation for a LEO satellite scenario with three ground terminals.
>
> Layout: Two-part diagram — a spatial geometry part on top, and a timing alignment diagram on the bottom.
>
> **Top part — Spatial Geometry:**
> - A satellite icon at the top center, labeled "LEO Satellite, h = 600 km, v = 7.56 km/s →" with a rightward arrow for orbital motion.
> - A light blue cone emanating from the satellite downward, representing the beam footprint, landing on a horizontal ground line.
> - On the ground line, the beam footprint is shown as a blue shaded region spanning 100 km.
> - Three terminal icons on the ground:
>   - UE_A at the center (directly below satellite), with a vertical dashed line up to satellite labeled "d_A = 600.0 km, τ_A = 2.000 ms"
>   - UE_C at 25 km offset, with a slightly angled dashed line labeled "d_C = 600.5 km, τ_C = 2.002 ms"
>   - UE_B at 50 km offset (beam edge), with a more angled dashed line labeled "d_B = 602.1 km, τ_B = 2.007 ms"
> - Horizontal distance annotations between terminals: "25 km" between A and C, "25 km" between C and B.
>
> **Bottom part — Timing Alignment (3 rows):**
> - A horizontal time axis at the top.
> - Three rows showing the progressive correction:
>
> Row 1 labeled "No TA Compensation":
> - Three colored bars (blue for UE_A, orange for UE_C, red for UE_B) showing when each UE's signal arrives at the satellite.
> - UE_A arrives at t₀ + 4.000 ms, UE_C at t₀ + 4.003 ms, UE_B at t₀ + 4.014 ms.
> - A gray vertical line marks the "Expected arrival window".
> - Red brackets show the total spread: 13.867 μs, labeled "Total spread = 13.9 μs ≫ CP = 4.69 μs"
>
> Row 2 labeled "After Common TA (4.000 ms)":
> - All three UEs advance their transmission by 4.000 ms.
> - UE_A signal arrives exactly at the expected window.
> - UE_C signal is offset by 3.5 μs (yellow bracket, labeled "3.5 μs < CP ✓")
> - UE_B signal is offset by 13.9 μs (red bracket, labeled "13.9 μs > CP ✗")
>
> Row 3 labeled "After Common TA + UE-specific TA":
> - Each UE applies its own additional TA correction.
> - All three signals arrive within a narrow green band centered on the expected window.
> - Green bracket labeled "All within CP tolerance ✓"
>
> Key elements: (1) three UEs at different distances in spatial diagram, (2) beam footprint coverage, (3) three-row progressive timing correction, (4) CP threshold annotation, (5) pass/fail markers for each correction level.
>
> Style: minimalist technical illustration, labeled with clear bold English text. Blue for UE_A and satellite beam, orange for UE_C, red for UE_B and timing violations, green for successful alignment, gray for reference lines. No decorative elements. Clean lines, high contrast.

📌 **图解说明**：
- 上部空间几何图：展示 LEO 卫星与三个终端的距离关系，直观看到路径差随水平距离增大 → 对应步骤 1、2
- 下部时序图第一行（无补偿）：三个终端的信号到达时间分散 13.9 μs，远超 CP 容限 → 对应步骤 1
- 下部时序图第二行（仅公共 TA）：大部分时延被消除，UE_C 勉强在 CP 内，但 UE_B 仍超标 → 对应步骤 3 第一级
- 下部时序图第三行（两级 TA）：所有终端信号在 CP 容限内精确对齐 → 对应步骤 3 完整补偿
- 卫星运动箭头提示动态更新需求 → 对应步骤 4

## 阶段五：边界与延伸（Boundary）

- **适用边界**：上述两级 TA 机制依赖终端具备 GNSS 定位能力。在 GNSS 不可用的场景下（如室内、GNSS 被干扰），终端无法自主计算与卫星的精确距离，需要回退到网络辅助的 TA 估计方案，精度会下降。此外，对于 GEO 卫星，虽然卫星相对静止（步骤 4 的动态问题缓解），但单程时延高达约 120 ms，对 HARQ（混合自动重传请求）的时序设计提出了根本性挑战，需要禁用或大幅修改 HARQ 机制。

- **常见误解**：
  (1) "NTN 的 TA 问题只是数值变大了"——不止如此。地面网络的 TA 是基站测量后下发的闭环机制，而 NTN 中由于 RTT 太大，闭环调整的响应速度不够，必须引入终端自主的开环补偿，这是机制层面的根本变化。
  (2) "LEO 卫星比 GEO 时延小，所以 TA 问题更轻"——LEO 的总时延确实更小，但 LEO 卫星高速运动导致时延变化率（delay rate）极高，TA 需要更频繁地更新，对跟踪算法的实时性要求反而更严格。

- **延伸方向**：3GPP Release 17/18 中 NTN 的具体 TA 信令设计（SIB19 中的公共 TA 参数）；NTN 中的 Random Access 流程修改（TA 如何影响 PRACH 设计）；多普勒频偏预补偿（与 TA 补偿并行的另一个关键 NTN 适配）；Regenerative vs Transparent payload 架构下 TA 处理的差异
