O3PRO - SCAFFOLDING

🧠 **O3PRO Design System: Expanded Implementation Material**

***

# 1. **Design Tokens: Core Variables for Theming**

Add these tokens in your `styles/tokens/colors.css`, `typography.css`, and `spacing.css` for global consistency.

```css
:root {
/* Color */
--slate-900: #0a0f1f;
--slate-800: #1e293b;
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--success-green: #10b981;
--warning-amber: #f59e0b;
--danger-red: #ef4444;
--info-blue: #3b82f6;
--card-bg: #22283b;
--surface-bg: #161a23;
--accent-hover: rgba(255,255,255,0.05);
--muted-gray: #6b7280;

/* Typography */
--font-display: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
--text-xs: 11px;
--text-sm: 13px;
--text-base: 15px;
--text-lg: 18px;
--text-xl: 24px;
--text-2xl: 32px;

/* Spacing */
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
}
```

***

# 2. **Layout / Structure (React + Styled-Components Example)**

## `Header.tsx`
```jsx
import styled from 'styled-components';

const Header = styled.header`
position: sticky;
top: 0;
z-index: 100;
background: var(--primary-gradient);
height: 180px;
display: flex;
align-items: center;
justify-content: space-between;
padding: var(--space-6) var(--space-8);
box-shadow: 0 4px 20px rgba(0,0,0,0.13);
`;

const TitleBlock = styled.div`
display: flex;
align-items: center;
gap: var(--space-4);

h1 {
font-size: var(--text-2xl);
font-family: var(--font-display);
color: #fff;
font-weight: 700;
background: var(--primary-gradient);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
}
`;

export default function HeaderComponent() {
return (
<Header>
<img src="/logo.svg" alt="Logo" height={54} />
<TitleBlock>
<h1>APEX Intelligence</h1>
<span className="user-avatar">M</span>
</TitleBlock>
{/* Actions/components here */}
</Header>
)
}
```

***

## `Tabs.tsx`
```jsx
import styled, { css } from 'styled-components';

const Tabs = styled.nav`
display: flex;
gap: var(--space-2);
padding: 0 var(--space-6);
background: var(--card-bg);
border-bottom: 1px solid rgba(255,255,255,0.11);
position: sticky;
top: 180px;
z-index: 90;
`;

const Tab = styled.button`
position: relative;
padding: var(--space-3) var(--space-4);
font-size: var(--text-sm);
font-weight: 600;
color: #c1c9e8;
background: none;
border: none;
cursor: pointer;
transition: color 0.2s;
border-radius: 6px 6px 0 0;

&:hover, &.active {
color: #fff;
background: var(--accent-hover);
}

&.active::after {
content: '';
position: absolute;
left: 10%;
right: 10%;
bottom: -2px;
height: 2px;
background: var(--primary-gradient);
border-radius: 2px;
}
`;

export const TabBar = ({ tabs, activeTab, onTabClick }) => (
<Tabs>
{tabs.map(tab => (
<Tab 
key={tab.id} 
className={activeTab === tab.id ? 'active' : ''} 
onClick={() => onTabClick(tab.id)}
aria-selected={activeTab === tab.id}
>
{tab.icon}{' '}{tab.label}
</Tab>
))}
</Tabs>
);
```

***

# 3. **Data Card Components (Score, Contact, AI Status)**

## `ScoreCard.tsx`
```jsx
const ScoreCard = styled.div`
background: var(--card-bg);
border-radius: 12px;
min-width: 120px;
height: 80px;
display: flex;
flex-direction: column;
align-items: center;
justify-content: center;
box-shadow: 0 1px 8px rgba(0,0,0,0.10);
margin: var(--space-2);
font-family: var(--font-display);

.score-value {
font-size: var(--text-xl);
font-weight: 700;
color: #fff;
line-height: 1;
}
.score-label {
font-size: var(--text-xs);
color: var(--muted-gray);
text-transform: uppercase;
font-weight: 500;
margin-top: var(--space-1);
}
`;

export const Score = ({ score, label, status }) => (
<ScoreCard>
<span className="score-value">{score}</span>
<span className="score-label">{label}</span>
{status && (
<span 
	style={{
		color: status === 'hot' ? 'var(--success-green)' :
		status === 'immediate' ? 'var(--danger-red)' : 'var(--muted-gray)',
		fontSize: 'var(--text-sm)',
		fontWeight: '600'
}}>
	{status.toUpperCase()}
</span>
)}
</ScoreCard>
);
```

***

## `ContactCard.tsx`
```jsx
const ContactCard = styled.div`
background: var(--card-bg);
border-radius: 10px;
padding: var(--space-6);
box-shadow: 0 2px 12px rgba(0,0,0,0.12);
display: flex;
flex-direction: column;
gap: var(--space-3);

span, a {
font-size: var(--text-base);
color: #e5e7ef;
line-height: 1.6;
display: flex;
align-items: center;
gap: var(--space-2);
font-family: var(--font-mono);
}

.copy-btn {
background: var(--accent-hover);
border-radius: 5px;
margin-left: var(--space-2);
cursor: pointer;
border: none;
outline: none;
padding: var(--space-1) var(--space-2);
transition: background 0.2s;
&:hover { background: var(--info-blue); color: #fff; }
}
`;

export const ContactInfo = ({ email, phone, company, title }) => (
<ContactCard>
<span><MailIcon /> {email} <button className="copy-btn">Copy</button></span>
<span><PhoneIcon /> {phone} <button className="copy-btn">Copy</button></span>
<span><BuildingIcon /> {company}</span>
<span><BriefcaseIcon /> {title}</span>
</ContactCard>
);
```

***

# 4. **Main Grid / Board Layout**

In `App.tsx`:
```jsx
import { HeaderComponent } from './Header';
import { TabBar } from './Tabs';
import { Score } from './ScoreCard';
import { ContactInfo } from './ContactCard';

const mainTabs = [
{id:'overview', icon:<InfoIcon/>, label:'Overview'},
{id:'personal', icon:<PersonIcon/>, label:'Personal'},
{id:'company', icon:<BuildingIcon/>, label:'Company'},
{id:'personality', icon:<BrainIcon/>, label:'Personality'},
{id:'content', icon:<MailIcon/>, label:'Content'},
];

export default function AppBoard() {
const [activeTab, setActiveTab] = useState('overview');
// demo data...
return (
<div>
	<HeaderComponent />
	<TabBar tabs={mainTabs} activeTab={activeTab} onTabClick={setActiveTab} />
	<main className="main-board" style={{
		display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '32px', margin: '32px'
	}}>
		<section>
			<ContactInfo 
			email="marshall.snover@colliers.com"
			phone="(925) 227-6205"
			company="Nick Goddard, Colliers International"
			title="Managing Partner / SVP"
			/>
			<Score score={91} label="Priority" status="immediate" />
			<Score score={80} label="Role" status="hot" />
			<Score score={95} label="Data" status="hot" />
		</section>
		<section>
			{/* Show tabbed content */}
		</section>
	</main>
</div>
)
}
```

***

# 5. **Modals, Dialogs & Overlays**

## `ContactDetailModal.tsx`
```jsx
const ModalOverlay = styled.div`
position: fixed; top:0; left:0; width:100vw; height:100vh;
background: rgba(24,28,40,0.66);
z-index: 200;
display: flex; align-items:center; justify-content: center;
animation: fadeIn 0.3s;
`;

const ModalCard = styled.div`
background: var(--card-bg);
border-radius: 18px;
box-shadow: 0 12px 64px rgba(0,0,0,0.26);
padding: var(--space-8);
min-width: 480px;
max-width: 96vw;
transition: transform 0.18s;
`;

export const ContactDetailModal = ({ open, onClose, children }) => (
open && <ModalOverlay onClick={onClose}>
<ModalCard onClick={e => e.stopPropagation()}>
{children}
</ModalCard>
</ModalOverlay>
);
```

***

# 6. **Accessibility Utilities**

**Focus States and ARIA:**
```css
:focus-visible {
outline: 3px solid var(--info-blue);
outline-offset: 2px;
border-radius: 4px;
}
.tab-nav [aria-selected="true"] {
font-weight: var(--weight-bold);
background: var(--primary-gradient);
color: #fff;
}
```

**ARIA example in React:**
```jsx
<Tab 
aria-selected={activeTab === tab.id}
aria-controls={`${tab.id}-panel`}
role="tab"
tabIndex={activeTab === tab.id ? 0 : -1}
// ...rest
>
{tab.label}
</Tab>
```

***

# 7. **Responsiveness (CSS/Styled/JS)**
```css
@media (max-width: 900px) {
.main-board {
grid-template-columns: 1fr;
}
}

@media (max-width: 600px) {
.header { flex-direction: column; }
.tab-nav { overflow-x: scroll; }
.main-board { margin: 0; }
.card, .score-card, .contact-card { padding: var(--space-4);}
}
```

***

# 8. **Microinteractions & Animations**

**Tab Switch:**
```jsx
{activeTab === 'overview' && <Fade>{/* ... */}</Fade>}
{activeTab === 'personal' && <Fade>{/* ... */}</Fade>}
```
With:
```jsx
import { CSSTransition } from 'react-transition-group';

const Fade = ({ children }) => (
<CSSTransition in appear timeout={150} classNames="fade">
{children}
</CSSTransition>
);
```
```css
.fade-enter { opacity: 0; }
.fade-enter-active, .fade-exit-active { transition: opacity 150ms; opacity: 1; }
.fade-exit { opacity: 1; }
.fade-exit-active { opacity: 0; }
```

***

# 9. **Theme Switcher**

Add a toggle to root styles (light/dark), e.g.:
```jsx
<button onClick={() => setTheme(theme => theme === 'dark' ? 'light' : 'dark')}>
	Switch Theme
</button>
```
In your CSS, use selectors/classes for `[data-theme="dark"]` and `[data-theme="light"]`.

***

# 10. **Production Setup & QA**

- **Linting:** ESLint/Prettier for code sanity
- **Tests:** Jest or React Testing Library for unit/components
- **Accessibility:** axe-core or Lighthouse audits
- **Performance:** Lazy-load components, optimize SVGs/images

***

# **Conclusion**

This expanded system gives you **concrete code scaffolds, design token files, component blueprints, accessibility utilities, and responsive overlays**—ready for rapid implementation in React/TypeScript and easily adaptable to a framework like Material UI or Chakra. For Figma/Sketch, use these specs as atomic components and global styles. 

**Need a complete Storybook, TypeScript interfaces, or integration in your codebase? Just specify your next step!**

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/7238fd9d-ba03-48b0-bfe6-17530c472d6b/O3PRO.md)