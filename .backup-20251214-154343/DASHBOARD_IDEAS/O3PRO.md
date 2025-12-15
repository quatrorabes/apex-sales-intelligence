O3-PRO

🧠 Here’s a **professional website designer’s strategy and enhancement recommendations** for your web page, based on the provided screenshots and code references:

***

## 1. **Color, Theme, and Visual Hierarchy**

- **Continue/Elevate the Modern Dark Theme:**  
  - Use a *deep slate* background (#0a0f1f / #1e293b), contrasted with *gradient banners* (blue → purple) for headers and tab highlights.
  - Maintain *high-contrast, clean typography*: large, bold titles, subtle header backgrounds, smooth transitions for tabs/buttons.

- **Accent Colors for Data Points:**  
  - Assign positive/urgent/neutral colors to badges (`green` for success, `red` for priority, `blue/purple` for active status).
  - Use subtle gradients / glow for actionable buttons and high-priority recommendations.

- **Make Use of Card-Based Layouts:**  
  - Each data segment ("Contact Information", "Scoring", "AI Status") should be in border-radius, lightly shadowed cards.
  - Ensure text never sits flush against card edges; use 20–32px padding inside cards.

***

## 2. **Layout & Section Organization**

- **Sticky Header and Tabbed Navigation:**  
  - Keep your top header sticky with a gradient fill, logo/icon left, page actions on right.
  - *Tabs* should remain clearly highlighted, with active tab in blue/violet gradient, hover effects for others.

- **Grid and Flexbox:**  
  - Use responsive *grid/flexbox* layouts:
    - Summary cards (like counts, scores, personalization) at top in a horizontal scroll/grid for quick stats.
    - Main content area divided into two columns (info and detail), with modal overlays for deep dives (see `ContactDetailModal.tsx`).

***

## 3. **Typography & Icons**

- **Typography Hierarchy:**  
  - H1 (Large, Weight 700, Gradient text for main names/titles).  
  - H2-H3 (Weight 600 or 500, slightly smaller, monotone).
  - Body Text (16px+, readable, semi-bold for data labels, normal weight for data).
  - Use monospaced font for emails/phones for clarity.

- **Iconography:**  
  - Use Lucide or similar icon sets for all labels (Mail, Phone, Company, Data points).
  - Small badge icons and avatar placeholders for contacts.

***

## 4. **User Experience Enhancements**

- **Copy-to-Clipboard & Actions:**  
  - Any field (email, phone, recommended action) should include a subtle copy icon, with a brief color-flash feedback on success.
- **Indication of Status/Enrichment:**  
  - “Last Enriched”, “Times Enriched”, “Status” badges, pulse with green/yellow for recent & urgent states.

- **Empty State & Loading Indicators:**  
  - Custom empty states (icon + “No Data Available” message), and animated loaders matching site accent color.

- **Context Cards in Modal:**  
  - Modal overlays (for contact details or intelligence) should fade in, with a drop shadow & center focus.
  - All tabs in the modal should keep their left alignment, show soft animation when switching.

***

## 5. **Advanced Enhancements and Features**

- **Responsive Design:**  
  - Ensure spacing, card arrangement, and tab behavior optimize for mobile and desktop.
- **Search and Filter:**  
  - Add clear placeholder text, floating filter/search bar at top of lists—match component color theme.
- **Personalization and Interactivity:**  
  - Show personalization indicators (e.g., “Immediate Priority”, “Top Opportunity”) using colored chips or left accent border on cards.

- **Context-Aware Tooltips and Help:**  
  - Each tab and component like scoring or personality should have hover or info help tooltips explaining meaning for new users.

***

## 6. **Sample Enhanced Structure:**

```plaintext
Header (sticky): [Logo] | [Title] | [Action Buttons]
Tabs (sticky subheader): Overview | Personal | Company | Personality | Chat Things | Content

Main Board (Grid):
- [Quick Stats Cards]: Priority | Role | Data
- [Contact Information Card]: Name, Email, Phone, Company, Title, Copy icons
- [Apex Scoring Board]: MDCP, RSS, and Priority scores with colored badge, recommended action
- [AI Intelligence Status]: Last enriched, enrichment count, enrichment button

Tabbed Modal (Contact Deep Dive):
- Overview: Personal summary, background (timeline), scores, enrichment data
- Personal: Rich details (education, career, network, recent mentions)
- Company: Mission, products/services, leadership, marketing position, news
- Personality: MBTI, key traits, written assessment
- Chat Things: Pain points, SBA drivers, insights, talking points
- Content: Outreach content builder (emails, call scripts, LinkedIn messages), copy icons, loading states

Footer (optional): Support, privacy links, secondary actions.
```

***

## 7. **Design Language References**
- *Inspiration*: Mix of modern dashboard suites (Linear, Superhuman, Notion), maintaining B2B seriousness and tech polish.

***

## 8. **Additional Recommendations**

- Use **subtle animation** for modal open/close, progress loading, tab switching.
- Offer **theme switcher** (dark/light).
- **Accessibility**: Ensure focus states, color contrast, alt text for icons.

***

### **Summary Table – Immediate Design Wins**

| Element                  | Enhancement Suggestion                             |
|--------------------------|----------------------------------------------------|
| Header                   | Gradient background, sticky, clear actions         |
| Tab Navigation           | Gradient highlight/active, subtle hover, sticky    |
| Data Cards/Stats         | Soft shadows, accent borders/icons, tight padding  |
| Modal Details            | Animated overlay, segmented tabs, copy icons       |
| Typography               | Clear hierarchy, accent color for keywords         |
| Interactivity            | Copy, search/filter, loading spinners, tooltips    |
| Mobile Responsiveness    | Shrink grid/cards, stack tabs, fixed action bar    |
| Accessibility            | Proper roles, ARIA tags, focus and label support   |

***

**Let me know if you want tailored CSS/JS component code, wireframes, or Figma-style design references for implementation!**

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/e94a6663-0f9c-4799-9d58-3bdb5c329194/CleanShot-2025-11-25-at-21.08.08-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=Qd5OX6i5UVSxIB3LQArM6P3zKcw%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/de411131-6143-41f0-a15c-7dd6719d5d10/CleanShot-2025-11-25-at-21.08.26-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=yktHviBcDRFWUdUPNTUv7TwNJfw%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/c93cc21d-f678-4a47-9e1f-4669f7848990/CleanShot-2025-11-25-at-21.09.02-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=3Y5bEbqUulXJzyuiwfR4Ba81qL0%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/d68ce608-5c1a-41c4-8550-69917745ef0b/CleanShot-2025-11-25-at-21.09.24-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=1ufJxhVq6GqGDmekW3t%2Frv%2BzDVI%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[5](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/518e6ac7-9208-49cf-8c28-0ab91682fa85/CleanShot-2025-11-25-at-21.08.41-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=2Q7E5f6tRNGN%2B0WFNp4Hq1Ub8Rs%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[6](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/708b67cb-4da9-4f43-89ff-1032c6595a1c/CleanShot-2025-11-25-at-21.09.12-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=KY%2BgG6zaG3a8A9Yi47civ37IGIM%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[7](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/03b29ed1-6231-4781-98f8-bf2483a21cc6/CleanShot-2025-11-25-at-21.08.51-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYE4KE37OI3&Signature=IHiMUEPeQt4FhAA72vPXNZXDQgo%3D&x-amz-security-token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCXG6QgOXGXyeQOjs5ybUHxMD9UYFGCYldjyZkSg1FABwIhAOxKq%2FKr2BHt%2Bt8KIm0moLhWCH%2BDYwEQ3lgoD7YnuI3NKvMECH4QARoMNjk5NzUzMzA5NzA1Igz9Dc8YY9E5qBGkXNgq0ASHXlMMjHsZhWr%2Btk9OkIo3FlJLTv5A2r9970VJuFMJZLi7JPy8jKvqqjPQO8mbdSurL%2F38%2BNBePFNoGIMxgvJMHNX4I53AvU3JIxSDiJE6mRkA%2Feq2hepOKiN03PRQVv44wcsr24InnWs3U1h7EUa9ml3%2BkuUDg3PS9GJ3Eb6EH8piusaOauL%2F5gpT5SAa%2BMxprQMw%2BK%2Bj24JGmjYCmR3tg95S0nJE6Elc0LQuqPYcYAj1KB1PRhMHsuKZgwZhwvNLfhkdpfXF9QUVifC%2B77xipF3MvRYYg8DWEepxzcSxPF8syuK8ej0tLuxUMIaA%2BBhlS5r0Jk8Cn1ZfDVUF%2BQfsDOYI6TThBnyFzk8mEvs7jXa8Fx%2FPId6qS7wAawrUUoxDyOz8NEZulJpdVm%2BgjuIYqCM6f8hvufBptgNxguIrL4qgtq8uFaFMQBCDph8%2FuX3F%2BM9Xnd0egl6Rmkcsx6hcHa2XP1j09kXQ4kWv5g3J17DKWYK424hdcoEje5WjUnc2%2FQYN80I%2FJxCnrFqB%2FbB%2B7zR6MkN6s4aw%2F%2BRErjOeAEcUCIFD1tLEz1AtM8lD7MnTM1rVKNSwCjcFW%2BPfmeu0KYNN%2FrTKDSzIgY%2FLxtSc%2BpSNhPo4UdkVPdbSsSY2uWN%2Btv%2BFx%2BipWefhnEUqBW2Bu8Lk%2BweJg6gQt26eOq5hO%2FsqogSpMA9Zt2I%2FFN9Pw%2BUbeVxoSSuWuwN49I1%2BBpRP8K0Hu7VmdYoZ9LZu5NWcybmi1CLipvvaxePQS1N%2Fb7uOfx2nf9XgEx7gKYGj8YCMMJqVmskGOpcBV9edD9x3f0bhVRuUomQo9P8PfU1YPGgJK66hvvlq9M37Mg0uws8NH5dGjmlX4j9lIkl6dFQNl9YUZIjwIc0UnZ20j7GF%2B2GvcHHNyMO%2BOquMLORCOddk%2Fz1P49vVHkSDiCZFey77Q5c0sBVM6eGKLXwOy1wO5StEJFHp39MBiPJkw15S4Zv5v21bldAmRc27wruGThbiuA%3D%3D&Expires=1764134501)
[8](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/6aa5de11-45ef-4cc5-b01d-d8a9002bc6c1/App.tsx)
[9](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/1be2cb27-df32-4eaa-9129-2bfb715fe386/ContactDetailModal.tsx)