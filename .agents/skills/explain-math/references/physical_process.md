# Explaining a mechanism driven by physical events

Refined with a learner on the Module 04 contact-anchor explanation. Use it for estimators, contact logic, termination and reset logic, and reward terms that respond to events.

1. **The physical decision.** What the robot or algorithm must decide, and why. Example: when one foot supports the body, odometry must decide when to move its ground reference to the other foot.
2. **Initial physical state.** Which parts are supported, what is moving, and what is known. No array indices yet.
3. **One full cycle in causal order:** physical state → sensor reading → calculation → internal decision → physical interpretation. Say what is recomputed every sample and what persists.
4. **Chronological frames** for the normal, false and accepted cases, as a picture sequence or GIF. Keep the old state visible until the algorithm actually commits the change.
5. **Each internal signal, defined operationally:** what creates it, what it stores, when it increments or resets, what happens at its threshold, and what it does **not** measure.
6. **Map the picture to the plot** before showing curves: which marker or transition is which physical event, and where to look first.
7. **Keep physical truth, computed estimate and algorithm belief visually separate.**
8. **Timing:** sample rate, samples needed, and delay to decision.
9. **Capability and limit:** what failure it prevents, what delay or cost it adds, and what remains unobservable.
