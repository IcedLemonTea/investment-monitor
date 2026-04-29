# Donezo UI Design Guidelines

This document outlines the foundational design system for the Donezo web application, ensuring consistency, accessibility, and a modern aesthetic.

## 1. Color Palette

The interface relies on a crisp, high-contrast palette anchored by forest green, ensuring professional yet approachable aesthetics.

### Primary Colors
* **Brand Green:** `#1B4D3E` (Used for primary buttons, active states, and dominant brand elements)
* **Action Green:** `#28A745` (Used for success states, positive trends, and secondary highlights)

### Neutral Colors
* **Background:** `#F4F7F6` (Off-white, reduces eye strain compared to pure white)
* **Card Surface:** `#FFFFFF` (Pure white for elevated elements)
* **Primary Text:** `#111827` (Near black for maximum readability)
* **Secondary Text:** `#6B7280` (Medium gray for timestamps, subtitles, and inactive states. Must meet 4.5:1 contrast ratio)
* **Borders/Dividers:** `#E5E7EB` (Light gray for subtle separation)

### Semantic Colors
* **Warning:** `#F59E0B` (Amber)
* **Danger/Error:** `#EF4444` (Red)

## 2. Typography

We utilize a clean, geometric sans-serif typeface (e.g., Inter or Roboto) to maintain high legibility across data-dense dashboards.

* **Font Family:** Inter, sans-serif
* **H1 (Page Titles):** 24px, Semi-Bold, Tracking: -1%
* **H2 (Card Titles):** 16px, Medium
* **Body (Primary):** 14px, Regular
* **Body (Secondary/Metadata):** 12px, Regular (Do not use smaller than 12px)

## 3. Spacing & Grid System

Adhere strictly to an 8-point grid system to establish vertical and horizontal rhythm. 

* **Base Unit:** 8px
* **Card Padding:** 24px (Standardize padding across all dashboard widgets)
* **Inter-component Spacing:** 16px or 24px
* **Layout Grid:** 12-column responsive fluid grid with 24px gutters.

## 4. Component Styling

### Surfaces & Elevation
* **Cards:** 100% opaque white background.
* **Border Radius:** 12px (Softens the interface without feeling overly playful).
* **Shadows:** Use subtle, highly diffused drop shadows (`box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);`). Avoid hard, dark borders.

### Buttons
* **Primary Button:** Solid Brand Green background, white text, 8px border radius. Hover state darkens the background by 10%.
* **Secondary Button:** Transparent background, Brand Green border (1px solid), Brand Green text. Hover state applies a 5% opacity Brand Green fill.

### Data Visualization
* **Rule of Solid Fills:** Never use hatched, dotted, or striped patterns in charts. 
* **Chart Colors:** Use variations of the primary green palette by altering opacity (e.g., 100%, 70%, 40%) or introducing analogous cool tones (teal, cyan) for distinction.
* **Tooltips:** Ensure all data points have interactive hover states displaying exact numerical values.