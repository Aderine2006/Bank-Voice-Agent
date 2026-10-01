'use client';

import { Briefcase, IndianRupee, Calendar, User, Building2 } from 'lucide-react';

interface ProfileCardProps {
  profile: any;
}

export default function ProfileCard({ profile }: ProfileCardProps) {
  const fields = [
    {
      key: 'requested_loan_amount',
      label: 'Loan Amount',
      icon: IndianRupee,
      format: (val: number) => `₹${(val || 0).toLocaleString('en-IN')}`,
    },
    {
      key: 'monthly_income',
      label: 'Monthly Income',
      icon: Briefcase,
      format: (val: number) => `₹${(val || 0).toLocaleString('en-IN')}`,
    },
    {
      key: 'employment_type',
      label: 'Employment',
      icon: Building2,
      format: (val: string) => val || 'Not specified',
    },
    {
      key: 'loan_purpose',
      label: 'Purpose',
      icon: User,
      format: (val: string) => val || 'Not specified',
    },
    {
      key: 'age',
      label: 'Age',
      icon: Calendar,
      format: (val: number) => val ? `${val} years` : 'Not specified',
    },
  ];

  const hasData = fields.some((f) => profile[f.key] !== null && profile[f.key] !== undefined);

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold mb-4 gradient-text">Customer Profile</h3>
      
      {!hasData ? (
        <p className="text-sm text-gray-500 text-center py-4">
          No information collected yet
        </p>
      ) : (
        <div className="space-y-3">
          {fields.map((field) => {
            const Icon = field.icon;
            const value = profile[field.key];
            const hasValue = value !== null && value !== undefined;

            return (
              <div
                key={field.key}
                className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-xl"
              >
                <Icon className={`w-5 h-5 ${hasValue ? 'text-primary-500' : 'text-gray-600'}`} />
                <div className="flex-1">
                  <p className="text-xs text-gray-500">{field.label}</p>
                  <p className={`text-sm ${hasValue ? 'text-gray-100' : 'text-gray-600'}`}>
                    {field.format(value)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
