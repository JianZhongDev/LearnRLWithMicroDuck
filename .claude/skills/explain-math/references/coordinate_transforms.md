# Coordinate-transform protocol

This format was refined with a learner in Module 02, using the `head_camera` → `trunk_base` calculation at `head_yaw=+45°`.

1. **Overview first:** the source frame, destination frame, parent chain, and notation. For example, `T^A_B` converts coordinates from frame B into frame A. Say that a written product acts on a point from right to left.
2. **Draw the chain** (diagram): `camera → jaw → yaw-roll → neck-pitch → neck → trunk`.
3. **Child-to-parent order for the explanation:** start with the point in the child frame, apply the child's transform into its parent, and repeat up to the requested frame. Report the intermediate point in every frame, labelled with that frame. A root-to-leaf forward-kinematics implementation can be mentioned afterwards as equivalent.
4. **Define each quantity where it is used:** frames, translation (m), rotation axis and angle (rad or deg, sign convention), resulting coordinates.
5. **Rotation matrices symbolically first**, with explicit `cos(θ)` and `sin(θ)` entries, then the numeric matrix. If a transform combines a fixed model orientation with a joint rotation, show the composition and say which factor comes from which.
6. **Show the matrix-vector product and the translation addition** for each step.
7. Distinguish a frame origin from its axes, since a rotation moves directions, not the frame's own origin. Distinguish model or site frames from library conventions, such as OpenCV camera axes.
8. If you give only a final transform result, offer the full child-to-parent arithmetic in one line afterwards.
