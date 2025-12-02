import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config';
import { Save, RefreshCw, Package, Wrench, Gem, Target, Lightbulb, X, User, Building2 } from 'lucide-react';

interface UserPreferences {
	user_id: string;
	products: string[];
	services: string[];
	value_propositions: string[];
	target_customers: string[];
	personal_differentiators: string[];
	company_differentiators: string[];
}

export default function WhyMeTab() {
	const [preferences, setPreferences] = useState<UserPreferences>({
		user_id: 'default_user',
		products: [],
		services: [],
		value_propositions: [],
		target_customers: [],
		personal_differentiators: [],
		company_differentiators: [],
	});
	const [loading, setLoading] = useState(true);
	const [saving, setSaving] = useState(false);

	useEffect(() => {
		fetchPreferences();
	}, []);

	const fetchPreferences = async () => {
		try {
			const res = await fetch('${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/user/preferences');
			const data = await res.json();
			if (data.success && data.preferences) {
				setPreferences(data.preferences);
			}
		} catch (err) {
			console.error('Failed to load preferences:', err);
		} finally {
			setLoading(false);
		}
	};

	const savePreferences = async () => {
		setSaving(true);
		try {
			const res = await fetch('${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/user/preferences', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(preferences),
			});
			const data = await res.json();
			if (data.success) {
				alert('✅ Preferences saved!');
			} else {
				alert('❌ Save failed: ' + data.error);
			}
		} catch (err) {
			console.error('Save error:', err);
			alert('❌ Network error');
		} finally {
			setSaving(false);
		}
	};

	const addItem = (field: keyof UserPreferences) => {
		setPreferences({
			...preferences,
			[field]: [...(preferences[field] as string[]), ''],
		});
	};

	const updateItem = (field: keyof UserPreferences, idx: number, value: string) => {
		const items = [...(preferences[field] as string[])];
		items[idx] = value;
		setPreferences({ ...preferences, [field]: items });
	};

	const removeItem = (field: keyof UserPreferences, idx: number) => {
		const items = [...(preferences[field] as string[])];
		items.splice(idx, 1);
		setPreferences({ ...preferences, [field]: items });
	};

	if (loading) {
		return (
			<div style={{ padding: 40, textAlign: 'center', color: '#9ca3af' }}>
				Loading preferences...
			</div>
		);
	}

	return (
		<div style={{ padding: '32px 0' }}>
			{/* Header */}
			<div
				style={{
					marginBottom: 32,
					background: 'linear-gradient(135deg, rgba(79,70,229,0.25), rgba(147,51,234,0.25))',
					borderRadius: 16,
					padding: '32px 40px',
					border: '1px solid rgba(99,102,241,0.3)',
				}}
			>
				<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
					<div>
						<h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: '#e5e7eb' }}>
							<Target size={28} style={{ display: 'inline', marginRight: 12 }} />
							Why Me? - Value Proposition Builder
						</h1>
						<p style={{ fontSize: 15, color: '#d1d5db' }}>
							Define your unique value proposition for AI-powered personalization
						</p>
					</div>
					<div style={{ display: 'flex', gap: 12 }}>
						<button
							onClick={fetchPreferences}
							style={{
								padding: '12px 20px',
								borderRadius: 10,
								border: '1px solid rgba(148,163,184,0.5)',
								background: 'rgba(15,23,42,0.6)',
								color: '#e5e7eb',
								fontSize: 14,
								fontWeight: 600,
								cursor: 'pointer',
								display: 'flex',
								alignItems: 'center',
								gap: 8,
							}}
						>
							<RefreshCw size={16} />
							Reload
						</button>
						<button
							onClick={savePreferences}
							disabled={saving}
							style={{
								padding: '12px 24px',
								borderRadius: 10,
								border: '2px solid rgba(34,197,94,0.6)',
								background: saving
									? 'rgba(71,85,105,0.5)'
									: 'linear-gradient(135deg, rgba(34,197,94,0.3), rgba(16,185,129,0.3))',
								color: '#e5e7eb',
								fontSize: 14,
								fontWeight: 700,
								cursor: saving ? 'not-allowed' : 'pointer',
								display: 'flex',
								alignItems: 'center',
								gap: 8,
							}}
						>
							<Save size={16} />
							{saving ? 'Saving...' : 'Save All'}
						</button>
					</div>
				</div>
			</div>

			{/* Content Grid */}
			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 24 }}>
				<Section
					title="Products"
					icon={<Package size={20} />}
					items={preferences.products}
					onAdd={() => addItem('products')}
					onUpdate={(idx, val) => updateItem('products', idx, val)}
					onRemove={(idx) => removeItem('products', idx)}
					placeholder="e.g., SBA 504 loans"
					description="What products do you offer?"
				/>
				<Section
					title="Services"
					icon={<Wrench size={20} />}
					items={preferences.services}
					onAdd={() => addItem('services')}
					onUpdate={(idx, val) => updateItem('services', idx, val)}
					onRemove={(idx) => removeItem('services', idx)}
					placeholder="e.g., Free consultation"
					description="What services do you provide?"
				/>
				<Section
					title="Value Propositions"
					icon={<Gem size={20} />}
					items={preferences.value_propositions}
					onAdd={() => addItem('value_propositions')}
					onUpdate={(idx, val) => updateItem('value_propositions', idx, val)}
					onRemove={(idx) => removeItem('value_propositions', idx)}
					placeholder="e.g., 10% down vs 30%"
					description="What makes you unique?"
				/>
				<Section
					title="Target Customers"
					icon={<Target size={20} />}
					items={preferences.target_customers}
					onAdd={() => addItem('target_customers')}
					onUpdate={(idx, val) => updateItem('target_customers', idx, val)}
					onRemove={(idx) => removeItem('target_customers', idx)}
					placeholder="e.g., Commercial bankers"
					description="Who do you serve?"
				/>
				<Section
					title="Your Personal Edge"
					icon={<User size={20} />}
					items={preferences.personal_differentiators}
					onAdd={() => addItem('personal_differentiators')}
					onUpdate={(idx, val) => updateItem('personal_differentiators', idx, val)}
					onRemove={(idx) => removeItem('personal_differentiators', idx)}
					placeholder="e.g., 20 years SBA experience"
					description="What makes YOU unique?"
				/>
				<Section
					title="Company Differentiators"
					icon={<Building2 size={20} />}
					items={preferences.company_differentiators}
					onAdd={() => addItem('company_differentiators')}
					onUpdate={(idx, val) => updateItem('company_differentiators', idx, val)}
					onRemove={(idx) => removeItem('company_differentiators', idx)}
					placeholder="e.g., Top 10 SBA lender"
					description="What makes your COMPANY unique?"
				/>
			</div>

			{/* Instructions */}
			<div
				style={{
					marginTop: 40,
					background: 'rgba(34,197,94,0.08)',
					borderRadius: 12,
					padding: 24,
					border: '1px solid rgba(34,197,94,0.3)',
				}}
			>
				<h3 style={{ fontSize: 16, fontWeight: 600, color: '#22c55e', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
					<Lightbulb size={18} />
					How This Works
				</h3>
				<ul style={{ color: '#d1d5db', fontSize: 14, lineHeight: 1.8, listStyle: 'inside' }}>
					<li>Add up to 5 items in each category</li>
					<li>These values are used during contact enrichment to personalize Sections 10 & 11</li>
					<li>The AI matches your products/services to each contact's specific needs</li>
					<li>Content generation (emails, calls) will emphasize relevant value props</li>
					<li><strong>Personal Edge</strong>: Your unique skills, experience, credentials</li>
					<li><strong>Company Differentiators</strong>: Your company's competitive advantages</li>
					<li>Changes here affect all future enrichments and content generation</li>
				</ul>
			</div>
		</div>
	);
}

function Section(props: {
	title: string;
	icon: React.ReactNode;
	items: string[];
	onAdd: () => void;
	onUpdate: (idx: number, value: string) => void;
	onRemove: (idx: number) => void;
	placeholder: string;
	description: string;
}) {
	const { title, icon, items, onAdd, onUpdate, onRemove, placeholder, description } = props;

	return (
		<div
			style={{
				background: 'rgba(15,23,42,0.6)',
				borderRadius: 12,
				padding: 24,
				border: '1px solid rgba(148,163,184,0.25)',
			}}
		>
			<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
				<div>
					<div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
						{icon}
						<h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb' }}>{title}</h3>
					</div>
					<p style={{ fontSize: 13, color: '#9ca3af' }}>{description}</p>
				</div>
				<button
					onClick={onAdd}
					style={{
						padding: '8px 16px',
						borderRadius: 6,
						border: '1px solid rgba(148,163,184,0.4)',
						background: 'rgba(99,102,241,0.15)',
						color: '#e5e7eb',
						fontSize: 13,
						fontWeight: 600,
						cursor: 'pointer',
					}}
				>
					+ Add
				</button>
			</div>

			<div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
				{items.map((item, idx) => (
					<div key={idx} style={{ display: 'flex', gap: 8 }}>
						<input
							type="text"
							value={item}
							onChange={(e) => onUpdate(idx, e.target.value)}
							placeholder={`${placeholder} #${idx + 1}`}
							style={{
								flex: 1,
								padding: '10px 14px',
								borderRadius: 6,
								border: '1px solid rgba(148,163,184,0.3)',
								background: 'rgba(30,41,59,0.6)',
								color: '#e5e7eb',
								fontSize: 14,
								outline: 'none',
							}}
						/>
						<button
							onClick={() => onRemove(idx)}
							style={{
								padding: '10px 14px',
								borderRadius: 6,
								border: '1px solid rgba(220,38,38,0.5)',
								background: 'rgba(220,38,38,0.15)',
								color: '#f87171',
								cursor: 'pointer',
							}}
						>
							<X size={16} />
						</button>
					</div>
				))}

				{items.length === 0 && (
					<p style={{ textAlign: 'center', color: '#64748b', fontSize: 13, padding: '16px 0' }}>
						No {title.toLowerCase()} added yet
					</p>
				)}
			</div>
		</div>
	);
}
