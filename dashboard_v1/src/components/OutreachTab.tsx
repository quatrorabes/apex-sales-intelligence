import EmailDrafter from './EmailDrafter';

interface OutreachTabProps {
    contactId: number;
    contactName: string;
    contactEmail?: string;
}

export default function OutreachTab({ contactId, contactName, contactEmail }: OutreachTabProps) {
    return (
        <div>
            <div className="mb-6">
                <h2 className="text-xl font-bold text-white mb-2">Email Outreach</h2>
                <p className="text-gray-400">Generate personalized emails using AI + your profile</p>
            </div>
            <EmailDrafter 
                contactId={contactId} 
                contactName={contactName}
                contactEmail={contactEmail}
            />
        </div>
    );
}
