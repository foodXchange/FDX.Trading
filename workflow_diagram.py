import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.5, 'FDX Trading - Business Workflow', 
        fontsize=20, fontweight='bold', ha='center')
ax.text(5, 9, 'Data Relationships Overview', 
        fontsize=14, ha='center', style='italic')

# Define colors
color_buyers = '#4CAF50'
color_suppliers = '#2196F3'
color_products = '#FF9800'
color_orders = '#9C27B0'
color_finance = '#F44336'

# Main entities with record counts
entities = [
    # (x, y, width, height, label, count, color)
    (1, 7, 1.8, 1, 'BUYERS', '22', color_buyers),
    (1, 5, 1.8, 1, 'REQUESTS', '85', color_buyers),
    (1, 3, 1.8, 1, 'PROPOSALS', '56', color_buyers),
    
    (4, 7, 1.8, 1, 'SUPPLIERS', '23,206', color_suppliers),
    (4, 5, 1.8, 1, 'PRODUCTS', '224', color_products),
    (4, 3, 1.8, 1, 'PRICE BOOK', '218', color_products),
    
    (7, 7, 1.8, 1, 'ORDERS', '166', color_orders),
    (7, 5, 1.8, 1, 'ORDER ITEMS', '549', color_orders),
    (7, 3, 1.8, 1, 'SHIPPING', '271', color_orders),
    
    (4, 1, 1.8, 0.8, 'INVOICES', '263', color_finance),
]

# Draw entities
for x, y, w, h, label, count, color in entities:
    # Box
    box = FancyBboxPatch((x, y), w, h, 
                         boxstyle="round,pad=0.05",
                         facecolor=color, 
                         edgecolor='darkgray',
                         alpha=0.3,
                         linewidth=2)
    ax.add_patch(box)
    
    # Label
    ax.text(x + w/2, y + h*0.65, label, 
           fontsize=11, fontweight='bold', 
           ha='center', va='center')
    
    # Count
    ax.text(x + w/2, y + h*0.35, count + ' records', 
           fontsize=9, ha='center', va='center',
           style='italic')

# Draw arrows showing relationships
arrows = [
    # (x1, y1, x2, y2, label)
    (2.8, 7.5, 4, 7.5, ''),  # Buyers -> Suppliers
    (1.9, 6, 1.9, 5, ''),    # Buyers -> Requests
    (1.9, 4, 1.9, 3, ''),    # Requests -> Proposals
    (2.8, 3.5, 4, 3.5, ''),  # Proposals -> Price Book
    (5.8, 7.5, 7, 7.5, ''),  # Suppliers -> Orders
    (5.8, 5.5, 7, 5.5, ''),  # Products -> Order Items
    (4.9, 4, 4.9, 1.8, ''),  # Price Book -> Invoices
    (7.9, 6, 7.9, 5, ''),    # Orders -> Order Items
    (7.9, 4, 7.9, 3, ''),    # Order Items -> Shipping
]

for x1, y1, x2, y2, label in arrows:
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', 
                           mutation_scale=20,
                           linewidth=1.5,
                           color='gray',
                           alpha=0.6)
    ax.add_patch(arrow)

# Add workflow stages at bottom
stages = [
    (0.5, 0.3, 'SOURCING'),
    (2.5, 0.3, 'PROPOSALS'),
    (4.5, 0.3, 'PRODUCTS'),
    (6.5, 0.3, 'FULFILLMENT'),
    (8.5, 0.3, 'FINANCIAL'),
]

for x, y, stage in stages:
    ax.text(x, y, stage, fontsize=10, fontweight='bold',
           ha='center', color='darkblue',
           bbox=dict(boxstyle="round,pad=0.3", 
                    facecolor='lightblue', alpha=0.3))

# Add statistics box
stats_text = """Database Statistics:
• Total Tables: 46
• Total Records: 26,306+
• Linked Products: 222
• Active Suppliers: 51"""

ax.text(9.5, 2, stats_text, fontsize=9,
       bbox=dict(boxstyle="round,pad=0.5", 
                facecolor='lightyellow', alpha=0.5),
       ha='right', va='bottom')

# Add phase status
phase_text = """Phase Status:
✓ Phase 1: Core Relations
○ Phase 2: Product Flow
○ Phase 3: Orders
○ Phase 4: Compliance
○ Phase 5: Financial"""

ax.text(0.5, 2, phase_text, fontsize=9,
       bbox=dict(boxstyle="round,pad=0.5", 
                facecolor='lightgreen', alpha=0.3),
       ha='left', va='bottom')

plt.tight_layout()
plt.savefig('workflow_diagram.png', dpi=150, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
plt.savefig('workflow_diagram.pdf', bbox_inches='tight',
           facecolor='white', edgecolor='none')

print("Workflow diagram saved as:")
print("  - workflow_diagram.png")
print("  - workflow_diagram.pdf")

plt.show()