import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

# Fix Intelligence tab - salesSection fallback
old_sales = '''            {salesCards.length > 0 ? salesCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)} color="text-orange-400">
                <BulletList items={s.content} color="text-orange-400" />
              </Card>
            )) : (
              <Card title="Sales Intelligence" icon={<TrendingUp size={18} />}>
                <p>No sales intelligence available. Enrich this contact to generate insights.</p>
              </Card>
            )}'''

new_sales = '''            {salesCards.length > 0 ? salesCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)} color="text-orange-400">
                <BulletList items={s.content} color="text-orange-400" />
              </Card>
            )) : salesSection ? (
              <Card title="Sales Intelligence" icon={<TrendingUp size={18} />} color="text-orange-400">
                <div className="text-gray-300 whitespace-pre-wrap text-sm">{salesSection}</div>
              </Card>
            ) : (
              <Card title="Sales Intelligence" icon={<TrendingUp size={18} />}>
                <p className="text-gray-400">No sales intelligence available. Enrich this contact to generate insights.</p>
              </Card>
            )}'''

content = content.replace(old_sales, new_sales)

# Fix Professional tab - personSection fallback
old_person = '''            {personCards.length > 0 ? personCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)}>
                <BulletList items={s.content} />
              </Card>
            )) : (
              <Card title="Overview" icon={<User size={18} />}>
                <DataRow label="Name" value={`${contact.firstname} ${contact.lastname}`} />
                <DataRow label="Title" value={contact.title} />
                <DataRow label="Company" value={contact.company} />
                <DataRow label="Email" value={contact.email} />
                <DataRow label="Phone" value={contact.phone || 'N/A'} />
              </Card>
            )}'''

new_person = '''            {personCards.length > 0 ? personCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)}>
                <BulletList items={s.content} />
              </Card>
            )) : personSection ? (
              <Card title="Professional Profile" icon={<User size={18} />}>
                <div className="text-gray-300 whitespace-pre-wrap text-sm">{personSection}</div>
              </Card>
            ) : (
              <Card title="Overview" icon={<User size={18} />}>
                <DataRow label="Name" value={`${contact.firstname} ${contact.lastname}`} />
                <DataRow label="Title" value={contact.title} />
                <DataRow label="Company" value={contact.company} />
                <DataRow label="Email" value={contact.email} />
                <DataRow label="Phone" value={contact.phone || 'N/A'} />
              </Card>
            )}'''

content = content.replace(old_person, new_person)

# Fix Company tab - companySection fallback
old_company = '''            {companyCards.length > 0 ? companyCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)} color="text-emerald-400">
                <BulletList items={s.content} color="text-emerald-400" />
              </Card>
            )) : (
              <Card title="Company" icon={<Building2 size={18} />}>
                <DataRow label="Company" value={contact.company} />
                <p className="mt-2 text-[#8b919a]">No company data available.</p>
              </Card>
            )}'''

new_company = '''            {companyCards.length > 0 ? companyCards.map((s, i) => (
              <Card key={i} title={s.title} icon={getIcon(s.title)} color="text-emerald-400">
                <BulletList items={s.content} color="text-emerald-400" />
              </Card>
            )) : companySection ? (
              <Card title="Company Intelligence" icon={<Building2 size={18} />} color="text-emerald-400">
                <div className="text-gray-300 whitespace-pre-wrap text-sm">{companySection}</div>
              </Card>
            ) : (
              <Card title="Company" icon={<Building2 size={18} />}>
                <DataRow label="Company" value={contact.company} />
                <p className="mt-2 text-gray-400">No company data available.</p>
              </Card>
            )}'''

content = content.replace(old_company, new_company)

file.write_text(content)
print("✅ Added raw section fallbacks!")
