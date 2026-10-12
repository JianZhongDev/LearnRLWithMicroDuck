"""Turn simulator frames into short captioned GIFs, and render static model views.

Captions matter: a GIF should say what is happening ("t=0.40 s  env 0  FELL ->
reset") so the learner can connect a visible event to a number in a plot.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _font(size: int):
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def caption_frames(
    frames: Sequence[np.ndarray],
    captions: Sequence[str],
    alert: Sequence[bool] | None = None,
) -> list[np.ndarray]:
    """Draw a caption bar on top of each frame. `alert[i]` turns the bar red."""
    out = []
    for i, frame in enumerate(frames):
        img = Image.fromarray(np.asarray(frame)).convert("RGB")
        draw = ImageDraw.Draw(img)
        size = max(12, img.height // 18)
        bar_h = int(size * 1.6)
        hot = bool(alert[i]) if alert is not None else False
        draw.rectangle([0, 0, img.width, bar_h], fill=(200, 50, 50) if hot else (31, 41, 51))
        draw.text((8, (bar_h - size) // 2), captions[i] if i < len(captions) else "", fill="white", font=_font(size))
        out.append(np.asarray(img))
    return out


def save_gif(frames: Sequence[np.ndarray], path: str | Path, fps: float = 12.5,
             hold_last: float = 1.0) -> Path | None:
    """Save frames as a looping GIF; the last frame is held so the end state is readable."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not len(frames):
        print(f"[duckkit] no frames to save, skipped {path.name} (rendering unavailable or render=False)")
        return None
    images = [Image.fromarray(np.asarray(f)).convert("RGB") for f in frames]
    duration = int(1000 / fps)
    durations = [duration] * len(images)
    durations[-1] = int(duration + hold_last * 1000)
    images[0].save(path, save_all=True, append_images=images[1:], duration=durations, loop=0, optimize=True)
    print(f"saved animation: {path} ({len(images)} frames)")
    return path


def model_snapshot(
    xml_path: str | Path,
    keyframe: str | None = None,
    qpos: np.ndarray | None = None,
    width: int = 480,
    height: int = 360,
    distance: float = 0.6,
    azimuth: float = 135.0,
    elevation: float = -20.0,
) -> np.ndarray:
    """Render one image of a plain MuJoCo model (no mjlab), e.g. to show a pose."""
    import mujoco

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)
    if keyframe is not None:
        key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, keyframe)
        if key_id < 0:
            raise ValueError(f"keyframe {keyframe!r} not found")
        mujoco.mj_resetDataKeyframe(model, data, key_id)
    if qpos is not None:
        data.qpos[:] = qpos
    mujoco.mj_forward(model, data)
    camera = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(model, camera)
    camera.distance, camera.azimuth, camera.elevation = distance, azimuth, elevation
    if model.nq >= 3:
        camera.lookat[:] = data.qpos[:3]
    with mujoco.Renderer(model, height, width) as renderer:
        renderer.update_scene(data, camera=camera)
        return renderer.render().copy()
