import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, ArrowStyle
import matplotlib.patches as patches

# 1. Generate Logo
fig, ax = plt.subplots(figsize=(3, 1))
ax.axis('off')
ax.text(0.5, 0.5, "RurTech", fontsize=28, fontweight='bold', color='#1e3a8a', ha='center', va='center', fontfamily='sans-serif')
ax.text(0.85, 0.5, "AI", fontsize=28, fontweight='bold', color='#e11d48', ha='center', va='center', fontfamily='sans-serif')
plt.savefig('logo.png', bbox_inches='tight', dpi=300, transparent=True)
plt.close()

# 2. Generate Accuracy Chart
labels = ['PII/PHI Redaction Precision', 'Structured Extraction Consistency', 'Semantic Version Compare Accuracy', 'Duplicate Hash Detection']
values = [98.5, 99.1, 91.0, 94.5]
colors = ['#1e40af', '#047857', '#0f766e', '#6d28d9']

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(labels, values, color=colors, height=0.6)
ax.set_xlim(0, 100)
ax.set_title('Agentic Stack Performance Metrics (%)', fontsize=14, fontweight='bold', pad=15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', length=0)

# Add values to bars
for bar in bars:
    width = bar.get_width()
    ax.text(width - 5, bar.get_y() + bar.get_height()/2, f'{width}%', 
            ha='center', va='center', color='white', fontweight='bold')

plt.tight_layout()
plt.savefig('accuracy.png', bbox_inches='tight', dpi=300)
plt.close()

# 3. Generate Architecture Flowchart
fig, ax = plt.subplots(figsize=(10, 5))
ax.axis('off')

def draw_box(ax, x, y, width, height, text, color):
    box = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1", 
                         ec="none", fc=color, mutation_scale=0.2)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', 
            color='white', fontweight='bold', fontsize=10, wrap=True)
    return x + width, y + height/2

# Draw boxes
c_input = '#475569'
c_agent = '#2563eb'
c_db = '#059669'
c_output = '#e11d48'

x0, y0 = draw_box(ax, 0.5, 3.5, 2, 1, "Input Source\n(Forms, SAEs, Audio)", c_input)
x1, y1 = draw_box(ax, 3.5, 3.5, 2, 1, "Anonymiser Agent\n(PII Tokenization)", c_agent)
x2, y2 = draw_box(ax, 6.5, 3.5, 2, 1, "Assessor Agent\n(Checklist Validation)", c_agent)
x3, y3 = draw_box(ax, 6.5, 1.5, 2, 1, "Classifier Agent\n(Severity Triage)", c_agent)
x4, y4 = draw_box(ax, 3.5, 1.5, 2, 1, "Vector RAG DB\n(CDSCO Guidelines)", c_db)
x5, y5 = draw_box(ax, 9.5, 2.5, 2, 1, "Final CDSCO PDF\n& NLP Conclusion", c_output)

# Draw arrows
style = "Simple, tail_width=1.5, head_width=6, head_length=8"
kw = dict(arrowstyle=style, color="gray")

# Input to Anonymiser
ax.add_patch(patches.FancyArrowPatch((x0, 4), (3.5, 4), connectionstyle="arc3,rad=.0", **kw))
# Anonymiser to Assessor
ax.add_patch(patches.FancyArrowPatch((5.5, 4), (6.5, 4), connectionstyle="arc3,rad=.0", **kw))
# Assessor to Classifier
ax.add_patch(patches.FancyArrowPatch((7.5, 3.5), (7.5, 2.5), connectionstyle="arc3,rad=.0", **kw))
# RAG to Assessor & Classifier
ax.add_patch(patches.FancyArrowPatch((4.5, 2.5), (4.5, 3.5), connectionstyle="arc3,rad=.0", **kw))
ax.add_patch(patches.FancyArrowPatch((5.5, 2), (6.5, 2), connectionstyle="arc3,rad=.0", **kw))
# Assessor to Output
ax.add_patch(patches.FancyArrowPatch((8.5, 4), (10.5, 3.5), connectionstyle="arc3,rad=.0", **kw))
# Classifier to Output
ax.add_patch(patches.FancyArrowPatch((8.5, 2), (10.5, 2.5), connectionstyle="arc3,rad=.0", **kw))

ax.set_title('RurTech Multi-Agent Orchestration Architecture', fontsize=14, fontweight='bold', pad=20)
ax.set_xlim(0, 12)
ax.set_ylim(0, 5)
plt.tight_layout()
plt.savefig('architecture.png', bbox_inches='tight', dpi=300)
plt.close()

print("Diagrams generated successfully!")
