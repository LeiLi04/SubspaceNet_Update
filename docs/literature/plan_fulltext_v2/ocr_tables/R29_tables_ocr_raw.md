# OCR dump for R29 (10.1109/JSEN.2023.3275318) tables

PDF: `docs/literature/fulltext/subscription/10.1109_jsen.2023.3275318.pdf`

Pages (0-indexed): 7, 8, 9


## Page 8 (PDF index 7)

Image: `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_fulltext_v2/ocr_tables/R29_p08.png`

```
14716 IEEE SENSORS JOURNAL, VOL. 23, NO. 13, 1 JULY 2023
0 0 0
—Truth —Truth
1000} . . oF 1000 x 1000 } are
F 2000 ° + 2000 F 2000
z oO = =
& 3000} } 3000 E 3000}
5000 “ “ . 7 5000 “ " “ 5000 “ “
0 90 180 270 360 0 90 180 270 360 0 90 180 270 360
Bearing angle (°) Bearing angle (°) Bearing angle (°)
(a) (b) (c)
0 0
oat exe
" ~~ ~FVB-AEKF
1000 1000 1
F 2000 F 2000 1
& 3000 & 3000 |
4000 4000 |
5000 5000
0 90 180 270 360 0 90 180 270 360
Bearing angle (°) Bearing angle (°)
(d) (e)
Fig. 2. Bearing angle tracking results of (a) CBF, (b) EKF, (c) SH-AEKF, (d) VB-AEKF, and (e) FVB-AEKF.
140 . .
TABLE V
AVERAGE RMSES AND MEANS OF THE RUN TIME IN ONE TIME STEP 120
OF THE CBF, EKF, VB-AEKF, AND FVB-AEKF 100
CBF _EKF SH-AEKF _VB-AEKF _FVB-AEKF 5 8
RMSE, (°) 27.55 1.52 1.24 1.09 1.10 Z 60
Mean ofrun 991 0.05 0.06 0.85 0.30 °
time (ms) _—__ 20
0
. : : 0 1000 2000» 3000» 4000-5000
estimates of the FVB-AEKF at all time steps, and Fig. 3(b) Times (s)
gives the partially magnified results for details. Table V shows 4 (a)
the average RMSEs and the mean of the run time in one ——EKF
time step. The results of the CBF, the EKF, SH-AEKF, and 5) arr
VB-AEKF are also given for comparison. _ | = RBAEKS \
Fig. 3 and the average RMSEs results in Table V show bs | \ f
that similar to the conclusion in the previous subsection, the g > IA
DOA tracking methods EKF, VB-AEKF, and FVB-AEKF “ A, | \
converged after a period of time. The tracking precision of ' hh AVVA .
SH-AEKF is superior to that of EKF. The VB-AEKF and vA “ .
the FVB-AEKF provide the most high-precision tracking even °) 1900. 2000 3000. 4000.~-~-5000
during the existence of the strong noise, while the CBF was Times (s)
invalid during this time. The superior performance of the (b)
proposed VB-AEKF and the FVB-AEKF was verified again. Fig. 3. RMSEs of (a) CBF and (b) EKF, SH-AEKF, VB-AEKF, and
Table V also shows that the CBF cost the longest time FVB-AEKF at all time steps.
because it needs to scan all bearing angles in space. The EKF
cost the least time because of its simple computation. Since the
SH-AEKF cost time to estimate the MNCM, the runtime of it performance of the VB-AEKF and the FVB-AEKF were
was longer than EKF. The VB-AEKF cost more time than EKF almost the same. The superiority of FVB-AEKF in terms of
and SH-AEKF because of its iteration process. The run time of computational efficiency and precision was then verified. The
the FVB-EKF decreased by 65% compared to the VB-AEKF. conclusion above is consistent with the theoretical analysis in
The reason is that the FVB-AEKF significantly reduces the Section IV. In addition, it should be noticed that, although the
computations of the FLOPs of trigonometric functions with © FVB-EKF cost more time than EKF and SH-AEKF, FVB-EKF
high computational complexity. What is more, the tracking provided more accurate tracking than EKF and SH-AEKF.
Authorized licensed use limited to: Universita degli Studi di Bologna. Downloaded on February 19,2026 at 13:42:34 UTC from IEEE Xplore. Restrictions apply.
```


## Page 9 (PDF index 8)

Image: `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_fulltext_v2/ocr_tables/R29_p09.png`

```
ZHANG et al.: FVB-AEKF FOR ROBUST UNDERWATER DIRECTION-OF-ARRIVAL TRACKING 14717
| _ al } j TABLE VI
Q ABEESs OF THE CBF, EKF, SH-AEKF, VB-AEKF, AND FVB-AEKF
a ee ‘ABEE (°)
' Data CBF  EKF SH-AEKF VB-AEKF FVB-AEKF
é Rawdata 13.2 8.2 71 63 63
: : Y as = With noise 19.9 12.2 7.3 6.5 6.5
Maes velocity was measured to be constant at 1544 m/s at the depth
(a) from 0 to 20 m with a conductivity, temperature, depth (CTD)
North profiler before the experiment.
a) #2 In order to provide the true bearing angle of the target rela-
Hey OTTO #1 Hydrophone tive to the circular hydrophone array for reference, the acoustic
0 EL signal emission system and the underwater buoy system were
BY eS nas #12 equipped with Global Positioning Systems (GPS). The GPSs
recorded the locations of the acoustic signal emission system
#6Q Oui Pst and the underwater buoy system every second. Considering the
me. O w10 bearing angle of the target is measured clockwise with respect
= 0 to the north, the bearing angle trajectory is calculated by the
GPS data.
®) B. Comparison of CBF, EKF, VB-AEKF, and FVB-AEKF
Fig. 4. Configuration of the underwater buoy system. (a) Photograph for DOA Tracking
of the underwater buoy system. (b) Configuration of the UCA and the .
compass system. The VB-AEKF and the FVB-AEKF were tested using
the experimental data of all 7500 s. The CBF-based DOA
VI. EXPERIMENTAL RESULTS estimation, the EKF, SH-AEKF, VB-AEKF, and FVB-AEKF
. ae were also carried out for comparison. The parameters are set to
A. Experimental Setup and Descrip tion ; be the same as those in the simulation. In order to numerically
The data from an acoustic experiment in the South China compare the precision of the bearing angle estimation, the
Sea m July 2021 was used to test the FVB-AEKF. An acoustic bearing angle estimation error (BEE) and the averaged BEE
signal emission system fixed on a ship that consists of a (ABEE) were defined as the performance metrics, which are
signal generator, a power amplifier, and an acoustic emission given as follows:
transducer was considered as a target. The signal generator .
and the power amplifier were deployed on the board and the BEE (k) = \& - oF Ps| (29)
acoustic emission transducer was placed 3 m under the sea x
surface. The electric signal output by the signal generator 1 A 2
was amplified by the power amplifier and then transduced ABEE (k) = K x (4 ~ oe °s) (30)
to the acoustic signal by the acoustic emission transducer. kel
The ship equipped with the acoustic signal emission sys- where 6, is the bearing angle estimate at time k and oGPs is
tem kept moving when an acoustic signal at 170 Hz was _ the true bearing angle obtained by the GPS data.
emitted continuously for 7 500 s with a sound source level The trajectories obtained by the CBF, EKF, SH-AEKF,
of 145 dB. VB-AEKF, and FVB-AEKF are shown in Fig. 5(a). The
An underwater buoy system shown in Fig. 4(a) was placed BEEs and the ABEEs are shown in Fig. 5(b) and Table VI,
at 20 m under the sea surface before the experiment. The respectively. Specifically, considering the complexity of the
distance from it to the acoustic signal emission system satisfied actual underwater environment, the CBF obtained bearing
the far-field assumption. A uniform circular hydrophone array angles every 10 s by using ten measurements as snapshots for a
with a radius of 1 m with 12 elements and a digital acquisition higher precision [7]. However, this higher precision is obtained
system was fixed on the underwater buoy. Elements 1 to at the expense of the real-time tracking capability. In order
12 were placed counterclockwise around the periphery of the to further test the robustness of the proposed FVB-AEKF to
circle. Considering the underwater buoy system rotated with unknown measurement noise, a period of Gaussian noise with
the waves, a compass system was fixed on it as shown in _ the covariance of 27 p was added to the raw measurement data
Fig. 4(b) to measure the bearing of hydrophone 1 to offset from 2600 to 3000 s, and then the methods were tested again.
the rotation angle. In Fig. 4(b), the rectangle represents the The results are shown in Fig. 5(c) and (d) and Table VI. The
compass system, and g (measured clockwise with respect black dotted lines in Fig. 5(c) and (d) denote the beginning
to the north) represents the bearing of element 1. During and ending times of the added noise.
emitting the acoustic signal, the digital acquisition system Fig. 5(a) and (b) show that the trajectories obtained by
sampled the output of the circular hydrophone array at a_ all methods using raw experimental data fluctuated around
frequency of 8 192 Hz and the compass system measured _ the true trajectory due to the effect of the underwater envi-
the bearing angles of hydrophone 1 every second. The sound ronmental noise. Fig. 5(a) and (b) and Table VI shows
Authorized licensed use limited to: Universita degli Studi di Bologna. Downloaded on February 19,2026 at 13:42:34 UTC from IEEE Xplore. Restrictions apply.
```


## Page 10 (PDF index 9)

Image: `/Users/lilei/PycharmProjects/SubspaceNet_Update/docs/literature/plan_fulltext_v2/ocr_tables/R29_p10.png`

```
14718 IEEE SENSORS JOURNAL, VOL. 23, NO. 13, 1 JULY 2023
0 —_
inn =e “| -=aF
1000 || —cBF ee —EKF
—— EKF 7a ———~ SH-AEKF
2000 | |—SH-AEKF re 7 30) VB-AEKF
—— VB-AEKF =F —— FVB-AEKF
& 3000 | |——FVB-AEKF raf cS l
2 = 20
FS 4000 <3 a 1
5000 ry y
| 10 Oar LANNE | }
= t y by iy
roooy SR PARR YT
-60 -30 0 30 60 0 2000 4000 6000
Bearing angle (°) Time (s)
(a) (b)
0 : 7 i 40 pr r 7
——EKF _ ~~ SH-AEKF
2000 | |—SH-AEKF a 30) |__VB-AEKF
= ——VB-AEKF ————sie —— FVB-AEKF
@ 3000 \ —FVB-AEKF ——=_ _| cS l
2 4000 ee 3 20
e SS = ih\ {
5000 > 7 k Mi
6000 aan HY bey } A \j |
7000 Se 1¥ ANY ; Vict rt AN
-60 -30 0 30 60 ° 2000 4000 6000
Bearing angle (°) Time (s)
(c) (d)
Fig. 5. Experimental results of CBF-based DOA estimation, EKF, SH-AEKF, VB-AEKF, and FVB-AEKF. (a) Trajectories obtained using raw data.
(b) BEEs obtained using raw data. (c) Trajectories obtained using the data with added noise. (d) BEEs obtained using the data with added noise.
that the VB-AEKF and the FVB-AEKF provided the most TABLE VII
accurate tracking of all the methods. The reason is that the RUN TIMES IN ONE TIME STEP OF CBF, EKF, SH-AEKF,
VB-AEKE and the FVB-AEKF not only predict the bear- VB-AEKF, AND FVB-AEKF
ing angle of the target using the kinematic model of the Run time (ms)
underwater target but also accurately estimate the MNCMs. Data CBF EKF  SH-AEKF  VB-AEKF  FVB-AEKF
The tracking precision of SH-AEKF is lower than VB-AEKF Rawdata 1.12. O11 0.13 0.70 0.34
and FVB-AEKF because the VB iteration process pro- With noise 1.08 0.11 0.14 0.75 0.35
vided more accurate MNCMs than the Sage-Husa algorithm.
The trajectory obtained by the EKF fluctuated more than
SH-AEKF, VB-AEKF, and FVB-AEKF due to the mismatch- shows once again that the FVB-EKF can provide higher
ing between the known and stationary MNCM assumption computational efficiency than VB-EKF while the performance
and the actual unknown and unstable MNCM. The CBF-based _ loss introduced by replacing the VB-AEKF with the FVB-EKF
DOA estimation provided the trajectory with the largest error can be ignored. The EKF and SH-AEKF cost less time than
because of ignoring the kinematic information of the under- the FVB-EKF, but provide DOA trajectories with larger errors.
water target. Thus, FVB-AEKF shows superiority in terms of robustness
The trajectories obtained using the data with added noise and precision.
given in Fig. S(c) and (d) show a similar conclusion to
the above. Furthermore, the VB-AEKF and FVB-AEKE still VII. CONCLUSION
provided robust tracking even after the added noise presented, The robust underwater DOA tracking with a nonlinear
while the performance of the EKF and the CBF-based DOA measurement model in the scenario of unknown measure-
estimation obviously degraded. The performance of SH-AEKF ment noise is studied in this article. First, for the sake of
is also slightly affected by the added noise, but the preci- accurate tracking and minimum underwater acoustic resource
sion of SH-AEKF is lower than VB-AEKF and FVB-AEKE. _ utilization, the kinematic model of the underwater target by
The ABEEs obtained using the data with added noise given bearing angle and the nonlinear measurement model based
in Table VI show the superiority of the VB-AEKF and on the received signal of a UCA are designed. Then, based
FVB-AEKF in the precision again. on the determined model, the algorithm of VB-AEKF for
The run time in the one time step of the CBF-based DOA robust underwater DOA tracking with unknown measurement
estimation, the EKF, the VB-AEKF, and the FVB-AEKF are _ noise is given. Finally, by deriving the equivalent process with
shown in Table VII. The run time of the FVB-EKF decreased less computations of VB-AEKF, the FVB-AEKF for DOA
by half compared to the VB-AEKF in both the process of tracking with nonlinear and high-dimensional measurement is
the raw data and that of the data with added noise. This proposed. The FVB-AEKF improves computational efficiency
Authorized licensed use limited to: Universita degli Studi di Bologna. Downloaded on February 19,2026 at 13:42:34 UTC from IEEE Xplore. Restrictions apply.
```
