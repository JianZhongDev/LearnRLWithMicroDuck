"""Module map and batch schematic for L05; no simulation."""
import duckkit as dk
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
dk.use_style()
fig, ax = plt.subplots(figsize=(12, 5))
ax.set(xlim=(0, 12), ylim=(0, 5))
ax.axis("off")

def box(x, y, w, h, title, subtitle, today=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.04",
        fc="#fff1dc" if today else "#e8edf3", ec="#e8833a" if today else "#9aa5b1", lw=1.5))
    ax.text(x+w/2, y+h*.66, title, ha="center", va="center", fontsize=12, weight="bold")
    ax.text(x+w/2, y+h*.27, subtitle, ha="center", va="center", fontsize=10)

def arrow(start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.5))

ax.text(6, 4.7, "Module 08: simulator to reinforcement learning environment", ha="center", fontsize=15, weight="bold")
for x, title, sub in [(0.2,"Observe","readings + commands"),(3.2,"Policy acts","joint targets"),
                       (6.2,"Simulate","robot moves"),(9.2,"Score & check","reward + ended?")]:
    box(x, 3.15, 2.6, .9, title, sub)
for x in [2.8, 5.8, 8.8]:
    arrow((x, 3.6), (x+.4, 3.6))
ax.plot([10.5,10.5,1.5,1.5], [3.1,2.75,2.75,3.1], color="#6b7280")
ax.text(6, 2.43, "Repeat for each robot; reset a copy when its episode ends", ha="center", fontsize=10)
box(.6,.7,4.7,1.1,"L05 TODAY: collect a batch","many robot copies × steps from each",True)
box(6.7,.7,4.7,1.1,"Update the policy","use the batch, then collect again",True)
arrow((6,2.32),(3,1.85))
arrow((5.35,1.25),(6.65,1.25))
ax.text(6,.13,"Schematic | L01 step • L02 endings • L03 reward • L04 observations • L05 training data",
        ha="center",fontsize=10)
dk.save_fig(fig,HERE/"map_L05.png")

fig, ax=plt.subplots(figsize=(10,4.3))
ax.set(xlim=(-1,12),ylim=(-1,6))
ax.axis("off")
for row in range(4):
    for col in range(3):
        ax.add_patch(Rectangle((col*1.2,3.5-row),1.1,.85,fc="#dcecff",ec="#7da7cf"))
    ax.text(-.2,3.92-row,["step 1","step 2","…","step T"][row],ha="right",va="center",fontsize=11)
for col,name in enumerate(["robot A","robot B","…"]):
    ax.text(col*1.2+.55,4.7,name,ha="center",fontsize=11)
ax.text(1.75,-.3,"Rows = steps; columns = robot copies",ha="center",fontsize=10)
ax.annotate("",xy=(6,2.5),xytext=(3.8,2.5),arrowprops=dict(arrowstyle="->",lw=2))
ax.text(8.7,3.3,"One cell stores one step's record",ha="center",weight="bold",fontsize=12)
ax.text(8.7,2.25,"observation used → action chosen\nreward received + episode ended?",ha="center",fontsize=11,linespacing=1.8)
ax.text(8.7,.55,"Filled batch → policy update\nNext collection reuses this space",ha="center",fontsize=11,linespacing=1.8)
ax.text(5.5,5.5,"Schematic: collect aligned records before updating",ha="center",weight="bold",fontsize=14)
dk.save_fig(fig,HERE/"steps_to_batch_L05.png")
