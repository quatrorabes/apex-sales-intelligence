#!/usr/bin/env python3

import React, { useState, useEffect } from 'react';
import { Save, RefreshCw, Plus, X, AlertCircle } from 'lucide-react';

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
		company_differentiators: []
	});
	const [loading, setLoading] = useState(false);
	const [saving, setSaving] = useState(false);
	const [message, setMessage] = useState('');
	
	const API_BASE = 'https://apex-intelligence-production.up.railway.app';
	
	// Load existing preferences
	useEffect(() => {
		loadPreferences();
	}, []);
	
	const loadPreferences = async () => {
		setLoading(true);
		try {
			const response = await fetch(`${API_BASE}/api/user/preferences`);
			const data = await response.json();
			
			if (data.success && data.preferences) {
				// Parse JSON strings to arrays
				setPreferences({
					user_id: data.preferences.user_id || 'default_user',
					products: JSON.parse(data.preferences.products || '[]'),
					services: JSON.parse(data.preferences.services || '[]'),
					value_propositions: JSON.parse(data.preferences.value_propositions || '[]'),
					target_customers: JSON.parse(data.preferences.target_customers || '[]'),
					personal_differentiators: JSON.parse(data.preferences.personal_differentiators || '[]'),
					company_differentiators: JSON.parse(data.preferences.company_differentiators || '[]')
				});
				setMessage('Preferences loaded');
			}
		} catch (error) {
			console.error('Error loading preferences:', error);
			setMessage('Failed to load preferences');
		} finally {
			setLoading(false);
		}
	};
	
	const savePreferences = async () => {
		setSaving(true);
		try {
			const response = await fetch(`${API_BASE}/api/user/preferences`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					user_id: preferences.user_id,
					products: JSON.stringify(preferences.products),
					services: JSON.stringify(preferences.services),
					value_propositions: JSON.stringify(preferences.value_propositions),
					target_customers: JSON.stringify(preferences.target_customers),
					personal_differentiators: JSON.stringify(preferences.personal_differentiators),
					company_differentiators: JSON.stringify(preferences.company_differentiators)
				})
			});
			
			const data = await response.json();
			
			if (data.success) {
				setMessage('✅ Preferences saved successfully!');
			} else {
				setMessage('❌ Failed to save preferences');
			}
		} catch (error) {
			console.error('Error saving preferences:', error);
			setMessage('❌ Error saving preferences');
		} finally {
			setSaving(false);
			setTimeout(() => setMessage(''), 3000);
		}
	};
	
	const addItem = (field: keyof UserPreferences) => {
		if (Array.isArray(preferences[field])) {
			setPreferences({
				...preferences,
				[field]: [...(preferences[field] as string[]), '']
			});
		}
	};
	
	const removeItem = (field: keyof UserPreferences, index: number) => {
		if (Array.isArray(preferences[field])) {
			const updated = [...(preferences[field] as string[])];
			updated.splice(index, 1);
			setPreferences({
				...preferences,
				[field]: updated
			});
		}
	};
	
	const updateItem = (field: keyof UserPreferences, index: number, value: string) => {
		if (Array.isArray(preferences[field])) {
			const updated = [...(preferences[field] as string[])];
			updated[index] = value;
			setPreferences({
				...preferences,
				[field]: updated
			});
		}
	};
	
	const renderSection = (
		title: string,
		field: keyof UserPreferences,
		placeholder: string,
		description: string,
		emoji: string
	) => (
		<div style={{
			backgroundColor: 'white',
			borderRadius: '12px',
			padding: '24px',
			boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
			border: '1px solid #e5e7eb'
		}}>
			<div style={{
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'space-between',
				marginBottom: '16px'
			}}>
				<div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
					<span style={{ fontSize: '24px' }}>{emoji}</span>
					<div>
						<h3 style={{
							fontSize: '18px',
							fontWeight: '600',
							margin: 0,
							color: '#111827'
						}}>
							{title}
						</h3>
						<p style={{
							fontSize: '14px',
							color: '#6b7280',
							margin: '4px 0 0 0'
						}}>
							{description}
						</p>
					</div>
				</div>
				<button
					onClick={() => addItem(field)}
					style={{
						padding: '8px 16px',
						backgroundColor: '#f3f4f6',
						border: 'none',
						borderRadius: '8px',
						cursor: 'pointer',
						display: 'flex',
						alignItems: 'center',
						gap: '6px',
						fontSize: '14px',
						fontWeight: '500',
						color: '#4b5563'
					}}
					onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
					onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
				>
					<Plus size={16} />
					Add
				</button>
			</div>
		
			<div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
				{Array.isArray(preferences[field]) && (preferences[field] as string[]).map((item, index) => (
					<div key={index} style={{
						display: 'flex',
						gap: '8px',
						alignItems: 'center'
					}}>
						<input
							type="text"
							value={item}
							onChange={(e) => updateItem(field, index, e.target.value)}
							placeholder={`${placeholder} ${index + 1}`}
							style={{
								flex: 1,
								padding: '10px 14px',
								border: '1px solid #d1d5db',
								borderRadius: '8px',
								fontSize: '14px',
								outline: 'none',
								transition: 'border-color 0.2s'
							}}
							onFocus={(e) => e.currentTarget.style.borderColor = '#6366f1'}
							onBlur={(e) => e.currentTarget.style.borderColor = '#d1d5db'}
						/>
						<button
							onClick={() => removeItem(field, index)}
							style={{
								padding: '8px',
								backgroundColor: '#fee2e2',
								border: 'none',
								borderRadius: '6px',
								cursor: 'pointer',
								color: '#dc2626',
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center'
							}}
							onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fca5a5'}
							onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fee2e2'}
						>
							<X size={18} />
						</button>
					</div>
				))}
		
				{(!Array.isArray(preferences[field]) || (preferences[field] as string[]).length === 0) && (
					<p style={{
						padding: '12px',
						backgroundColor: '#f9fafb',
						borderRadius: '8px',
						color: '#9ca3af',
						fontSize: '14px',
						textAlign: 'center',
						margin: 0
					}}>
						No items added yet. Click "Add" to start.
					</p>
				)}
			</div>
		</div>
	);
	
	return (
		<div style={{
			padding: '24px',
			maxWidth: '1400px',
			margin: '0 auto'
		}}>
			{/* Header */}
			<div style={{
				marginBottom: '32px',
				background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
				borderRadius: '16px',
				padding: '32px',
				color: 'white',
				boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.3)'
			}}>
				<div style={{
					display: 'flex',
					justifyContent: 'space-between',
					alignItems: 'start'
				}}>
					<div>
						<h1 style={{
							fontSize: '32px',
							fontWeight: 'bold',
							margin: '0 0 8px 0',
							display: 'flex',
							alignItems: 'center',
							gap: '12px'
						}}>
							🎯 Why Me? - Value Proposition Builder
						</h1>
						<p style={{
							fontSize: '16px',
							opacity: 0.9,
							margin: 0
						}}>
							Define your unique value proposition for AI-powered personalization
						</p>
					</div>
					<div style={{ display: 'flex', gap: '12px' }}>
						<button
							onClick={loadPreferences}
							disabled={loading}
							style={{
								padding: '12px 24px',
								backgroundColor: 'rgba(255, 255, 255, 0.2)',
								color: 'white',
								border: 'none',
								borderRadius: '8px',
								cursor: loading ? 'not-allowed' : 'pointer',
								fontWeight: '600',
								fontSize: '14px',
								display: 'flex',
								alignItems: 'center',
								gap: '8px',
								backdropFilter: 'blur(10px)',
								opacity: loading ? 0.5 : 1
							}}
						>
							<RefreshCw size={18} />
							Reload
						</button>
						<button
							onClick={savePreferences}
							disabled={saving}
							style={{
								padding: '12px 24px',
								backgroundColor: 'white',
								color: '#6366f1',
								border: 'none',
								borderRadius: '8px',
								cursor: saving ? 'not-allowed' : 'pointer',
								fontWeight: '600',
								fontSize: '14px',
								display: 'flex',
								alignItems: 'center',
								gap: '8px',
								opacity: saving ? 0.5 : 1
							}}
						>
							<Save size={18} />
							{saving ? 'Saving...' : 'Save All'}
						</button>
					</div>
				</div>
		
				{message && (
					<div style={{
						marginTop: '16px',
						padding: '12px',
						backgroundColor: 'rgba(255, 255, 255, 0.2)',
						borderRadius: '8px',
						backdropFilter: 'blur(10px)',
						display: 'flex',
						alignItems: 'center',
						gap: '8px'
					}}>
						<AlertCircle size={18} />
						{message}
					</div>
				)}
			</div>
		
			{/* Content Grid */}
			<div style={{
				display: 'grid',
				gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
				gap: '24px'
			}}>
				{renderSection(
					'Products',
					'products',
					'Product',
					'What products do you offer? (e.g., SBA 504 loans, Bridge financing)',
					'📦'
				)}
		
				{renderSection(
					'Services',
					'services',
					'Service',
					'What services do you provide? (e.g., Free consultation, Pre-approval)',
					'🛠️'
				)}
		
				{renderSection(
					'Value Propositions',
					'value_propositions',
					'Value Prop',
					'What makes you unique? (e.g., 10% down vs 30%, Fixed rates)',
					'💎'
				)}
		
				{renderSection(
					'Target Customers',
					'target_customers',
					'Target',
					'Who do you serve? (e.g., Medical practices, Manufacturers)',
					'🎯'
				)}
		
				{renderSection(
					'Personal Differentiators',
					'personal_differentiators',
					'Personal Edge',
					'Your personal strengths (e.g., 20+ years experience, Industry expert)',
					'⭐'
				)}
		
				{renderSection(
					'Company Differentiators',
					'company_differentiators',
					'Company Edge',
					'Your company strengths (e.g., Top 10 lender, $2B+ funded)',
					'🏢'
				)}
			</div>
		
			{/* Instructions */}
			<div style={{
				marginTop: '32px',
				padding: '24px',
				backgroundColor: '#f0fdf4',
				borderRadius: '12px',
				border: '1px solid #86efac'
			}}>
				<h3 style={{
					fontSize: '16px',
					fontWeight: '600',
					marginBottom: '12px',
					color: '#166534'
				}}>
					💡 How This Works
				</h3>
				<ul style={{
					margin: 0,
					paddingLeft: '20px',
					color: '#166534',
					fontSize: '14px',
					lineHeight: '24px'
				}}>
					<li>Add up to 5 items in each category</li>
					<li>These values are used during contact enrichment to personalize Section 10 & 11</li>
					<li>The AI matches your products/services to each contact's specific needs</li>
					<li>Content generation (emails, calls) will emphasize relevant value props</li>
					<li>Changes here affect all future enrichments and content generation</li>
				</ul>
			</div>
		</div>
	);
}
