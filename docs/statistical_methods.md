# Statistical Methods & Inference Formulations

## 1. Hypothesis Testing Framework

FlowPulse evaluates treatment effects against clearly specified null hypotheses ($H_0$):

$$\begin{aligned}
H_0 &: \theta_{\text{treatment}} - \theta_{\text{control}} = 0 \\
H_1 &: \theta_{\text{treatment}} - \theta_{\text{control}} \neq 0 \quad (\alpha = 0.05, \text{ two-sided})
\end{aligned}$$

---

## 2. Proportion Testing (Binary Metrics)

For metrics such as Activation Rate, Checkout Conversion Rate, and Retention:

### 2.1 Two-Proportion Pooled Z-Test
When comparing two independent proportions with sample sizes $N_c$ and $N_t$:
$$\hat{p}_c = \frac{X_c}{N_c}, \quad \hat{p}_t = \frac{X_t}{N_t}$$
$$\hat{p}_{\text{pool}} = \frac{X_c + X_t}{N_c + N_t}$$
$$\text{SE}_{\text{pool}} = \sqrt{\hat{p}_{\text{pool}}(1 - \hat{p}_{\text{pool}})\left(\frac{1}{N_c} + \frac{1}{N_t}\right)}$$
$$Z = \frac{\hat{p}_t - \hat{p}_c}{\text{SE}_{\text{pool}}}$$
The two-sided p-value is calculated as:
$$p = 2 \times \left(1 - \Phi(|Z|)\right)$$

### 2.2 Difference in Proportions Confidence Interval
The two-sided $100(1 - \alpha)\%$ confidence interval for absolute lift $\Delta = p_t - p_c$ uses unpooled standard error:
$$\text{SE}_{\text{unpooled}} = \sqrt{\frac{\hat{p}_c(1 - \hat{p}_c)}{N_c} + \frac{\hat{p}_t(1 - \hat{p}_t)}{N_t}}$$
$$\text{CI}_{1-\alpha}(\Delta) = [\Delta - Z_{1-\alpha/2}\text{SE}_{\text{unpooled}}, \Delta + Z_{1-\alpha/2}\text{SE}_{\text{unpooled}}]$$

### 2.3 Relative Lift Confidence Interval (Delta Method)
Relative lift is defined as $RL = \frac{p_t - p_c}{p_c} = \frac{p_t}{p_c} - 1 = RR - 1$.
Using the Delta Method on the logarithm of Relative Risk ($\ln RR$):
$$\text{Var}(\ln RR) \approx \frac{1 - \hat{p}_c}{N_c \hat{p}_c} + \frac{1 - \hat{p}_t}{N_t \hat{p}_t}$$
$$\text{CI}_{1-\alpha}(RR) = \exp\left( \ln\left(\frac{\hat{p}_t}{\hat{p}_c}\right) \pm Z_{1-\alpha/2} \sqrt{\text{Var}(\ln RR)} \right)$$
$$\text{CI}_{1-\alpha}(RL) = [\text{CI}_{\text{lower}}(RR) - 1, \text{CI}_{\text{upper}}(RR) - 1]$$

---

## 3. Continuous Metric Testing (Revenue & Duration)

### 3.1 Welch's T-Test
For comparing continuous metrics (e.g. 30-day ARPU in USD) where treatment and control groups exhibit unequal variances ($\sigma_c^2 \neq \sigma_t^2$):
$$t = \frac{\bar{Y}_t - \bar{Y}_c}{\sqrt{\frac{s_c^2}{N_c} + \frac{s_t^2}{N_t}}}$$
With Welch-Satterthwaite adjusted degrees of freedom:
$$\nu \approx \frac{\left( \frac{s_c^2}{N_c} + \frac{s_t^2}{N_t} \right)^2}{\frac{(s_c^2 / N_c)^2}{N_c - 1} + \frac{(s_t^2 / N_t)^2}{N_t - 1}}$$

### 3.2 Mann-Whitney U Test
A non-parametric test evaluating stochastic dominance between variants, robust against heavy-tailed or zero-inflated distributions.

---

## 4. Multiplicity Adjustments

When evaluating multiple secondary metrics simultaneously, FlowPulse applies:
- **Benjamini-Hochberg Procedure (FDR)**: Ranks raw p-values $p_{(1)} \le \dots \le p_{(m)}$ and finds the largest $k$ such that $p_{(k)} \le \frac{k}{m} \alpha$, controlling the False Discovery Rate.
- **Bonferroni Correction (FWER)**: Enforces conservative significance threshold $\alpha' = \frac{\alpha}{m}$.
