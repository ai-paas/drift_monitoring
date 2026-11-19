# CHART-REP-002 Guide

This chart explains autoencoder representation drift through reconstruction error, error trend, and latent-space separation.

Read in this order:

1. Summary card: p95 error `0.51`, threshold `0.36`, and latent AUC `0.84`.
2. Reconstruction-error distribution: current density shifts to higher error values than baseline.
3. Error trend: reconstruction error rises over time and exceeds threshold `0.36`.
4. Latent projection: baseline and current clusters separate in latent space.
5. Notes/legend: use as context only.

The chart-level interpretation should connect p95 error above threshold, increasing reconstruction error, and latent cluster separation as representation drift evidence.

Do not claim an operational root cause from autoencoder evidence alone. Mention that model capacity, reconstruction threshold calibration, and segment composition should be checked.
