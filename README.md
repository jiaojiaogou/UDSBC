# UDSBC
The Upstream-Downstream Scaled Bias Correction algorithm

By Jiaojiao Gou, Chiyuan Miao (Beijing Normal University)

UDSBC was developed to automaticly conduct the statistical post-processing to reduce model simulation bias for 
gauged rivers, upstream rivers, nested rivers and ungauged rivers, repectively.

For each gauged river reach, a gamma distribution parameterized function was used to map the observed streamflow (obs_data) 
and simulated streamflow (model_data) for the baseline period (e.g., 1961–1979) to the monthly simulated streamflow for the whole simulation 
period (sce_data, e.g., 1961–2018) by the maximum likelihood method. Then the bias-corrected streamflow was calculated using 
the scaled fitted gamma distribution (SDM or EQM method) for all cumulative density function values corresponding to the streamflow time series 
for each gauged river reach.

Upstream rivers refer to river reaches between the gauged river and the source of the gauged river. 
Nested rivers are similar to upstream rivers, but are located between two nested gauge stations. 
UDSBC allocated the bias of gauged river streamflow to each detected upstream/nested river based on the simulated streamflow amplitude 
because the gauged river streamflow is a spatial accumulation of streamflow from the upstream nested rivers. 
Ungauged rivers do not have any river network topology connection with gauged river sections. Following the principle of hydrological similarity, 
UDSBC allocated the mean bias of all gauged rivers to each ungauged river within a large river basin, such as the Yangtze river basin. 

**Using this code, the related literatures are suggested to be cited.

References:
Gou J.J., Miao C.Y*, Ni J.R., Duan Q.Y., Sorooshian S., Yan D.H., Xu Z.X., Borthwick Su L., Wu J.W., Wada Y. Warming climate and water withdrawal constrain natural river connectivity in China. 2022. (Under Review)

