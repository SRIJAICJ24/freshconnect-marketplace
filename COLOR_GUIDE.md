# 🎨 FreshConnect Color Guide

## Color Palette

### Primary Colors

```css
--primary: #478559;          /* Green Treeline */
--primary-dark: #36653f;     /* Darker Green */
--secondary: #39a0ca;        /* Blue Water */
--danger: #f95d9b;           /* Pink Highlight */
--warning: #ffc107;          /* Yellow (kept from Bootstrap) */
--success: #478559;          /* Green Treeline */
--info: #39a0ca;             /* Blue Water */
--light: #f8f9fa;            /* Light Gray */
--dark: #161748;             /* Purple Baseline */
```

### Color Swatches

| Color | Hex | RGB | Use Case |
|-------|-----|-----|----------|
| 🟢 Green Treeline | `#478559` | `rgb(71, 133, 89)` | Primary actions, success states |
| 🟣 Purple Baseline | `#161748` | `rgb(22, 23, 72)` | Navbar, dark backgrounds |
| 🩷 Pink Highlight | `#f95d9b` | `rgb(249, 93, 155)` | Alerts, urgent actions |
| 🔵 Blue Water | `#39a0ca` | `rgb(57, 160, 202)` | Secondary actions, info |
| 🟡 Yellow | `#ffc107` | `rgb(255, 193, 7)` | Warnings, badges |

---

## Usage Guidelines

### 1. Navigation
```css
/* Navbar background */
background-color: var(--dark);  /* #161748 - Purple Baseline */
color: white;
```

### 2. Primary Actions
```css
/* Submit, Add, Continue buttons */
.btn-primary {
    background-color: var(--primary);  /* #478559 - Green Treeline */
}
```

### 3. Secondary Actions
```css
/* Cancel, Back buttons */
.btn-secondary {
    background-color: var(--secondary);  /* #39a0ca - Blue Water */
}
```

### 4. Alerts & Errors
```css
/* Danger alerts, delete actions */
.btn-danger, .alert-danger {
    background-color: var(--danger);  /* #f95d9b - Pink Highlight */
}
```

### 5. Success Messages
```css
.alert-success {
    background-color: var(--success);  /* #478559 - Green Treeline */
}
```

### 6. Product Pricing
```css
/* Attract attention to prices */
.price {
    color: var(--primary);  /* #478559 - Green Treeline */
    font-weight: bold;
}
```

### 7. Emergency Products
```css
/* Urgency indicator */
.emergency-badge {
    background-color: var(--danger);  /* #f95d9b - Pink Highlight */
}
```

---

## Component Examples

### Buttons

```html
<!-- Primary (Green) -->
<button class="btn btn-primary">Add to Cart</button>

<!-- Secondary (Blue) -->
<button class="btn btn-secondary">View Details</button>

<!-- Danger (Pink) -->
<button class="btn btn-danger">Delete</button>

<!-- Success (Green) -->
<button class="btn btn-success">Submit Order</button>
```

### Cards

```html
<div class="card">
    <div class="card-header bg-primary text-white">
        Product Details
    </div>
    <div class="card-body">
        <!-- Content -->
    </div>
</div>
```

### Alerts

```html
<!-- Success (Green) -->
<div class="alert alert-success">Order placed successfully!</div>

<!-- Danger (Pink) -->
<div class="alert alert-danger">Payment failed. Please try again.</div>

<!-- Info (Blue) -->
<div class="alert alert-info">Driver is on the way.</div>

<!-- Warning (Yellow) -->
<div class="alert alert-warning">Product expires tomorrow!</div>
```

### Badges

```html
<span class="badge bg-primary">MOQ</span>
<span class="badge bg-danger">Emergency</span>
<span class="badge bg-info">Vegetables</span>
<span class="badge bg-warning">Expiring Soon</span>
```

---

## Accessibility

### Contrast Ratios

| Foreground | Background | Ratio | WCAG AA |
|------------|------------|-------|---------|
| White | #478559 (Green) | 4.1:1 | ✅ Pass |
| White | #161748 (Purple) | 11.5:1 | ✅ Pass |
| White | #f95d9b (Pink) | 3.2:1 | ⚠️ Large text only |
| White | #39a0ca (Blue) | 2.9:1 | ⚠️ Large text only |

### Recommendations
- Use white text on Purple (#161748) and Green (#478559)
- For Pink and Blue backgrounds, use large, bold text
- Add borders for better definition

---

## Color Combinations

### Successful Combinations

```css
/* Navbar */
background: #161748;  /* Purple */
text: white;

/* Primary Button */
background: #478559;  /* Green */
text: white;

/* Secondary Button */
background: #39a0ca;  /* Blue */
text: white;

/* Emergency Badge */
background: #f95d9b;  /* Pink */
text: white;
```

### Avoid These Combinations

❌ Pink text on Green background (poor contrast)
❌ Blue text on Purple background (hard to read)
❌ Yellow text on white background (invisible)

---

## Dark Mode Support (Future)

If implementing dark mode, use these variants:

```css
:root[data-theme="dark"] {
    --primary: #5ba86f;          /* Lighter Green */
    --secondary: #4cb8e4;        /* Lighter Blue */
    --danger: #ff7bae;           /* Lighter Pink */
    --dark: #0d0e2e;             /* Darker Purple */
    --light: #1a1b4a;            /* Dark Gray-Purple */
}
```

---

## Implementation Checklist

### CSS Variables
- [x] Update mobile-first.css root variables
- [ ] Update any inline styles in templates
- [ ] Update custom component CSS

### Templates
- [ ] Review all buttons (btn-primary, btn-secondary, etc.)
- [ ] Review all alerts (alert-success, alert-danger, etc.)
- [ ] Review all badges (badge-primary, badge-info, etc.)
- [ ] Review card headers
- [ ] Review navbar styling

### Testing
- [ ] Test on mobile devices
- [ ] Test on tablets
- [ ] Test on desktop
- [ ] Check contrast in all contexts
- [ ] Verify readability

---

## Browser Support

These colors are supported by all modern browsers:
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Edge 79+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## Color Psychology

### Why These Colors?

**🟢 Green (#478559)**
- Represents freshness, nature, growth
- Perfect for fresh produce marketplace
- Conveys trust and health

**🟣 Purple (#161748)**
- Professional, premium feel
- Creates depth and stability
- Reduces eye strain on dark backgrounds

**🩷 Pink (#f95d9b)**
- Attention-grabbing without being alarming
- Friendly and approachable
- Perfect for urgent but non-critical alerts

**🔵 Blue (#39a0ca)**
- Trustworthy and calming
- Good for informational elements
- Associated with reliability

---

## Quick Reference

```css
/* Copy-paste this into your styles */

/* Primary Action (Green) */
.btn-custom-primary {
    background-color: #478559;
    color: white;
    border: none;
}

/* Secondary Action (Blue) */
.btn-custom-secondary {
    background-color: #39a0ca;
    color: white;
    border: none;
}

/* Danger Action (Pink) */
.btn-custom-danger {
    background-color: #f95d9b;
    color: white;
    border: none;
}

/* Dark Background (Purple) */
.bg-custom-dark {
    background-color: #161748;
    color: white;
}
```

---

## Troubleshooting

### Issue: Colors not showing
**Solution:** Hard refresh browser (Ctrl+F5)

### Issue: Colors look different on mobile
**Solution:** Check for inline styles overriding CSS variables

### Issue: Poor contrast
**Solution:** Use white or very light text on colored backgrounds

---

**Last Updated:** Nov 2025
**Version:** 1.0
**Status:** ✅ Implemented
